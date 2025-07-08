from decimal import Decimal as D, ROUND_HALF_UP
import logging

from django.apps import apps
from django.conf import settings
from django.utils import timezone

import stripe


logger = logging.getLogger(__name__)
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
        self.quantity = kwargs.get("quantity")
        self.title = kwargs.get("title")
        self.price_incl_tax = kwargs.get("price_incl_tax")
        self.price_currency = kwargs.get("price_currency")

class Facade(object):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = "2020-03-02"

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
            return int(D(str(price)).quantize(D('1'), ROUND_HALF_UP))
        else:
            return int(D(str(price)).quantize(D('0.01'), ROUND_HALF_UP) * 100)


    def _get_raw_line_items(self, basket, shipping_method):
        raw_line_items = []

        for line in basket.all_lines():
            # This loop splits line into discounted and non-discounted ones
            for prices in line.get_price_breakdown():
                price_incl_tax, _, quantity = prices
                raw_line_items.append(
                    PaymentItem(
                        title=line.product.title,
                        price_incl_tax=price_incl_tax,
                        price_currency=line.price_currency,
                        quantity=quantity,
                    )
                )

        if basket.is_shipping_required() and shipping_method:
            price = shipping_method.calculate(basket)
            raw_line_items.append(
                PaymentItem(
                    title=shipping_method.name,
                    price_incl_tax=price.incl_tax,
                    price_currency=price.currency,
                    quantity=1,
                )
            )

        return raw_line_items

    def _prepare_line_item(self, name, amount, currency, quantity):
        prepared_line_item = {}

        if settings.STRIPE_USE_PRICES_API:
            prepared_line_item = {
                "price_data":  {
                    "product_data": {
                        "name": summary,
                    },
                    "currency": currency,
                    "unit_amount": amount,
                },
                "quantity": quantity,
            }
        else:
            prepared_line_item =  {
                "name": name,
                "amount": amount,
                "currency": currency,
                "quantity": quantity,
            }

        return prepared_line_item

    def _prepare_line_items(self, raw_line_items):
        prepared_line_items = []

        if settings.STRIPE_COMPRESS_TO_ONE_LINE_ITEM:

            name = ", ".join([
                f"{raw_line_item.quantity}x{raw_line_item.title}"
                for raw_line_item in raw_line_items
            ])
            amount = self.convert_to_cents(total.incl_tax, total.currency),
            currency = total.currency
            quantity = 1

            prepared_line_item = self._prepare_line_item(
                name, amount, currency, quantity
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

                prepared_line_item = self._prepare_line_item(
                    name, amount, currency, quantity
                )
                prepared_line_items.append(prepared_line_item)

        return prepared_line_items


    def _get_extra_session_metadata(
        self, session_metadata, raw_line_items, session_line_items,
    ):
        return {}

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

        discount_metadata = self._get_discount_metadata(raw_line_items)
        session_metadata.update({"discounts": discount_metadata})

        extra_session_metadata = self._get_extra_session_metadata(
            session_metadata, raw_line_items, session_line_items,
        )
        session_metadata.update(extra_session_metadata)

        return session_metadata

    def _get_extra_session_params(self, raw_line_items, session_line_items):
        return {}

    def _get_cancel_url(self):
        return settings.STRIPE_PAYMENT_CANCEL_URL.format(self.basket.id)

    def _get_success_url(self):
        return settings.STRIPE_PAYMENT_SUCCESS_URL.format(self.basket.id)

    def _get_capture_method(self):
        return "manual"

    def _get_session_mode(self):
        return "payment"

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
            "payment_method_types": ["card"],
            "line_items": session_line_items,
            "metadata": session_metadata,
            "success_url": success_url,
            "cancel_url": cancel_url,
            "payment_intent_data": {
                "capture_method": capture_method,
            },
        }

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
        basket.freeze()

        session = stripe.checkout.Session.create(**session_params)

        return session

    def retrieve_payment_intent(self, pi):
        return stripe.PaymentIntent.retrieve(pi)

    def capture(self, order_number, **kwargs):
        """
        If capture is set to `False` in charge, the charge will only be pre-authorized.
        One needs to use capture to actually charge the customer.

        """
        logger.info(f"Initiating Stripe payment capture for order #{order_number}")
        try:
            order = Order.objects.get(number=order_number)
            payment_source = Source.objects.get(order=order)

            # get charge_id from source
            charge_id = payment_source.reference

            stripe.PaymentIntent.modify(
                charge_id,
                receipt_email=order.user.email
            )
            stripe.PaymentIntent.capture(charge_id)

            # set captured timestamp
            payment_source.date_captured = timezone.now()
            payment_source.save()
            logger.info(
                "Payment for Order #%s (ID: %s) was captured via Stripe (ref: %s)" % (
                    order.number, order.id, charge_id
                )
            )

        except Source.DoesNotExist as e:
            logger.exception(f"Source error for Order #{order_number}")
            raise Exception(
                f"Capture failed: could not find Payment Source for Order #{order_number}"
            )

        except Order.DoesNotExist as e:
            logger.exception(f"Order error for Order  #{order_number}")
            raise Exception(
                f"Capture failed: Order #{order_number} does not exist"
            )
