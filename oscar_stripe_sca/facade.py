from decimal import Decimal as D, ROUND_HALF_UP
import logging

from django.apps import apps
from django.urls import reverse_lazy
from django.utils import timezone


import stripe

from . import settings
from .constants import (
    CAPTURE_METHOD_MANUAL,
    PAYMENT_METHOD_TYPE_CARD,
    SESSION_MODE_PAYMENT,
)
from .exceptions import MultipleTaxCodesInBasket


Source = apps.get_model("payment", "Source")
Order = apps.get_model("order", "Order")

# https://support.stripe.com/questions/which-zero-decimal-currencies-does-stripe-support
ZERO_DECIMAL_CURRENCIES = (
    "BIF",  # Burundian Franc
    "CLP",  # Chilean Peso
    "DJF",  # Djiboutian Franc
    "GNF",  # Guinean Franc
    "JPY",  # Japanese Yen
    "KMF",  # Comorian Franc
    "KRW",  # South Korean Won
    "MGA",  # Malagasy Ariary
    "PYG",  # Paraguayan Guaraní
    "RWF",  # Rwandan Franc
    "VND",  # Vietnamese Đồng
    "VUV",  # Vanuatu Vatu
    "XAF",  # Central African Cfa Franc
    "XOF",  # West African Cfa Franc
    "XPF",  # Cfp Franc
)


class PaymentItem:
    def __init__(self, **kwargs):
        self.title = kwargs.get("title")
        self.price_incl_tax = kwargs.get("price_incl_tax")
        self.price_currency = kwargs.get("price_currency")
        self.quantity = kwargs.get("quantity")
        self.tax_code = kwargs.get("tax_code")


class Facade(object):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = settings.STRIPE_API_VERSION
        self.logger = logging.getLogger(settings.STRIPE_LOGGER_NAME)

    @staticmethod
    def get_friendly_decline_message(error):
        return (
            "The transaction was declined by your bank. "
            "Please check your payment card details and try again."
        )

    @staticmethod
    def get_friendly_error_message(error):
        return "An error occurred when communicating with the payment gateway."

    def convert_to_cents(self, price, currency):
        """
        Convert price to cents with proper rounding, handling zero-decimal currencies.

        """
        if currency.upper() in ZERO_DECIMAL_CURRENCIES:
            return int(D(str(price)).quantize(D("1"), ROUND_HALF_UP))
        else:
            return int(D(str(price)).quantize(D("0.01"), ROUND_HALF_UP) * 100)

    def _get_default_product_tax_code(self):
        return settings.STRIPE_DEFAULT_PRODUCT_TAX_CODE

    def _get_product_tax_code(self, product):
        return settings.STRIPE_DEFAULT_PRODUCT_TAX_CODE  # Customize at will!

    def _get_shipping_tax_code(self):
        return settings.STRIPE_DEFAULT_SHIPPING_TAX_CODE

    def _choose_tax_code(self, raw_line_items):
        """Choose the singular tax code that should be applied to a
        compressed basket line, based on the passed `raw_line_items`.

        The default behavior is to refuse to choose, i.e. to raise
        an exception if different tax codes are found in the basket.

        Customize at will!

        """
        unique_tax_codes = list(set([
            item.tax_code for item in raw_line_items
        ]))
        unique_tax_codes_count = len(unique_tax_codes)
        if unique_tax_codes_count == 0:
            return self._get_default_product_tax_code()
        elif unique_tax_codes_count == 1:
            return unique_tax_codes[0]
        else:
            raise MultipleTaxCodesInBasket(
                "Basket contains products with different tax codes."
            )

    def _get_raw_line_items(self):
        raw_line_items = []

        for line in self.basket.all_lines():
            # This loop splits line into discounted and non-discounted ones
            for prices in line.get_price_breakdown():
                price_incl_tax, _, quantity = prices
                raw_line_items.append(
                    PaymentItem(
                        title=line.product.title,
                        price_incl_tax=price_incl_tax,
                        price_currency=line.price_currency,
                        quantity=quantity,
                        tax_code=self._get_product_tax_code(line.product),
                    )
                )

        if self.basket.is_shipping_required() and self.shipping_method:
            shipping_price = self.shipping_method.calculate(self.basket)
            raw_line_items.append(
                PaymentItem(
                    title=self.shipping_method.name,
                    price_incl_tax=shipping_price.incl_tax,
                    price_currency=shipping_price.currency,
                    quantity=1,
                    tax_code=self._get_shipping_tax_code(),
                )
            )

        return raw_line_items

    def _prepare_line_item(self, name, amount, currency, quantity, tax_code=None):
        prepared_line_item = {}

        if settings.STRIPE_USE_PRICES_API:
            product_data = {"name": name}
            if tax_code and settings.STRIPE_ENABLE_TAX_COMPUTATION:
                product_data.update({"tax_code": tax_code})

            prepared_line_item = {
                "price_data": {
                    "product_data": product_data,
                    "currency": currency,
                    "unit_amount": amount,
                },
                "quantity": quantity,
            }
        else:
            prepared_line_item = {
                "name": name,
                "amount": amount,
                "currency": currency,
                "quantity": quantity,
            }

        return prepared_line_item

    def _prepare_line_items(self, raw_line_items):
        prepared_line_items = []

        if settings.STRIPE_COMPRESS_TO_ONE_LINE_ITEM:

            name = ", ".join(
                [
                    f"{raw_line_item.quantity}x{raw_line_item.title}"
                    for raw_line_item in raw_line_items
                ]
            )
            amount = self.convert_to_cents(total.incl_tax, total.currency)
            currency = total.currency
            quantity = 1
            tax_code = self._choose_tax_code(raw_line_items)

            prepared_line_item = self._prepare_line_item(
                name, amount, currency, quantity, tax_code
            )
            prepared_line_items.append(prepared_line_item)

        else:
            for raw_line_item in raw_line_items:

                name = raw_line_item.title
                amount = self.convert_to_cents(
                    raw_line_item.price_incl_tax, raw_line_item.price_currency
                )
                currency = raw_line_item.price_currency
                quantity = raw_line_item.quantity
                tax_code = raw_line_item.tax_code

                prepared_line_item = self._prepare_line_item(
                    name, amount, currency, quantity
                )
                prepared_line_items.append(prepared_line_item)

        return prepared_line_items

    def _get_extra_session_metadata(
        self,
        session_metadata,
        raw_line_items,
        session_line_items,
    ):
        return {}  # Customize at will!

    def _get_discount_metadata(self):
        discounts = []

        # TODO: add site-wide offers data

        for voucher in self.basket.grouped_voucher_discounts:
            voucher_name = voucher["voucher"].name
            voucher_discount = voucher["discount"]
            discounts.append(f"{voucher_name} ({voucher_discount})")

        return ", ".join(discounts)

    def _build_session_metadata(self, raw_line_items, session_line_items):
        session_metadata = {}

        discount_metadata = self._get_discount_metadata()
        session_metadata.update({
            "discounts": discount_metadata,
        })

        extra_session_metadata = self._get_extra_session_metadata(
            session_metadata,
            raw_line_items,
            session_line_items,
        )
        session_metadata.update(extra_session_metadata)

        return session_metadata

    def _get_extra_session_params(
        self,
        session_params,
        raw_line_items,
        session_line_items,
    ):
        return {}  # Customize at will!

    def _get_tax_session_params(
        self,
        session_params,
        raw_line_items,
        session_line_items,
    ):
        tax_session_params = {
            "automatic_tax": {
                "enabled": True,
            },
        }
        return tax_session_params

    def _get_cancel_url(self):
        base_cancel_url = settings.STRIPE_PAYMENT_CANCEL_URL or (
            "{0}{1}".format(
                settings.STRIPE_RETURN_URL_BASE,
                reverse_lazy("checkout:stripe-cancel"),
            )
        )
        return base_cancel_url.format(self.basket.id)

    def _get_success_url(self):
        base_success_url = settings.STRIPE_PAYMENT_SUCCESS_URL or (
            "{0}{1}".format(
                settings.STRIPE_RETURN_URL_BASE,
                reverse_lazy("checkout:stripe-preview"),
            )
        )
        return base_success_url.format(self.basket.id)

    def _get_capture_method(self):
        return CAPTURE_METHOD_MANUAL

    def _get_session_mode(self):
        return SESSION_MODE_PAYMENT

    def _build_session_params(
        self, raw_line_items, session_line_items, session_metadata
    ):

        session_mode = self._get_session_mode()
        capture_method = self._get_capture_method()
        success_url = self._get_success_url()
        cancel_url = self._get_cancel_url()

        session_params = {
            "mode": session_mode,
            "customer_email": self.customer_email,
            "payment_method_types": [PAYMENT_METHOD_TYPE_CARD],
            "line_items": session_line_items,
            "metadata": session_metadata,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "payment_intent_data": {
                "capture_method": capture_method,
            },
        }

        if settings.STRIPE_ENABLE_TAX_COMPUTATION:
            tax_session_params = self._get_tax_session_params(
                session_params, raw_line_items, session_line_items
            )
            session_params.update(tax_session_params)

        extra_session_params = self._get_extra_session_params(
            session_params, raw_line_items, session_line_items
        )
        session_params.update(extra_session_params)

        return session_params

    def begin(self, customer_email, basket, total, shipping_method):
        self.customer_email = customer_email
        self.basket = basket
        self.total = total
        self.shipping_method = shipping_method

        raw_line_items = self._get_raw_line_items()
        session_line_items = self._prepare_line_items(raw_line_items)
        session_metadata = self._build_session_metadata(
            raw_line_items, session_line_items
        )
        session_params = self._build_session_params(
            raw_line_items, session_line_items, session_metadata
        )

        self.basket.freeze()

        session = stripe.checkout.Session.create(**session_params)

        return session

    def retrieve_payment_intent(self, payment_intent_id):
        return stripe.PaymentIntent.retrieve(payment_intent_id)

    def capture(self, order_number, **kwargs):
        """
        If `capture_method` is set to `manual` when creating the Stripe
        session, the charge will only be pre-authorized. In that case,
        one needs to use this `capture` method to actually charge the
        customer.

        """
        self.logger.info(f"Initiating Stripe payment capture for order #{order_number}")
        try:
            order = Order.objects.get(number=order_number)
            payment_source = Source.objects.get(order=order)

            # Get the charge identifier from the payment source
            charge_id = payment_source.reference

            stripe.PaymentIntent.modify(charge_id, receipt_email=order.user.email)
            stripe.PaymentIntent.capture(charge_id)

            # Set the capture timestamp
            payment_source.date_captured = timezone.now()
            payment_source.save()
            self.logger.info(
                "Payment for Order #%s (ID: %s) was captured via Stripe (ref: %s)"
                % (order.number, order.id, charge_id)
            )

        except Source.DoesNotExist as e:
            self.logger.exception(f"Source error for Order #{order_number}")
            raise Exception(
                f"Capture failed: could not find Payment Source for Order #{order_number}"
            )

        except Order.DoesNotExist as e:
            self.logger.exception(f"Order error for Order  #{order_number}")
            raise Exception(f"Capture failed: Order #{order_number} does not exist")
