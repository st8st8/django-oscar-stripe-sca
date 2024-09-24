import datetime
import logging

import stripe
from django.apps import apps
from django.conf import settings
from django.utils import timezone
from decimal import Decimal as D

from oscar_stripe_sca import utils

logger = logging.getLogger(__name__)
Source = apps.get_model('payment', 'Source')
Order = apps.get_model('order', 'Order')

# https://support.stripe.com/questions/which-zero-decimal-currencies-does-stripe-support
ZERO_DECIMAL_CURRENCIES = (
    'BIF',  # Burundian Franc
    'CLP',  # Chilean Peso
    'DJF',  # Djiboutian Franc
    'GNF',  # Guinean Franc
    'JPY',  # Japanese Yen
    'KMF',  # Comorian Franc
    'KRW',  # South Korean Won
    'MGA',  # Malagasy Ariary
    'PYG',  # Paraguayan Guaraní
    'RWF',  # Rwandan Franc
    'VND',  # Vietnamese Đồng
    'VUV',  # Vanuatu Vatu
    'XAF',  # Central African Cfa Franc
    'XOF',  # West African Cfa Franc
    'XPF',  # Cfp Franc
)


class PaymentItem:
    def __init__(self, **kwargs):
        self.quantity = kwargs.get('quantity')
        self.title = kwargs.get('title')
        self.price_incl_tax = kwargs.get('price_incl_tax')
        self.price_currency = kwargs.get('price_currency')

class Facade(object):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.api_version = "2020-03-02"

    @staticmethod
    def get_friendly_decline_message(error):
        return 'The transaction was declined by your bank - please check your bankcard details and try again'

    @staticmethod
    def get_friendly_error_message(error):
        return 'An error occurred when communicating with the payment gateway.'

    def begin(self, customer_email, basket, total, shipping_method):
        multiplier = 1
        if total.currency.upper() in ZERO_DECIMAL_CURRENCIES:
            multiplier = 1
        else:
            multiplier = 100

        metadata = {
            "discounts": "",
        }

        for voucher in basket.grouped_voucher_discounts:
            metadata['discounts'] += "{0} ({1}), ".format(voucher['voucher'].name, voucher['discount'])

        all_line_items = []
        for line in basket.all_lines():
            # this loop will split line into discounted and non-discounted lines
            for prices in line.get_price_breakdown():
                price_incl_tax, _, quantity = prices
                all_line_items.append(
                    PaymentItem(
                        quantity=quantity,
                        title=line.product.title,
                        price_incl_tax=price_incl_tax,
                        price_currency=line.price_currency
                    )
                )

        if basket.is_shipping_required() and shipping_method:
            price = shipping_method.calculate(basket)
            all_line_items.append(
                PaymentItem(
                    quantity=1,
                    title=shipping_method.name,
                    price_incl_tax=price.incl_tax,
                    price_currency=price.currency
                )
            )

        # Four cases here.  Two versions of the Stripe API, and whether we want to compress the line items or not.
        if settings.STRIPE_COMPRESS_TO_ONE_LINE_ITEM:
            line_items_summary = ", ".join(["{0}x{1}".format(l.quantity, l.title) for l in all_line_items])
            if not settings.STRIPE_USE_PRICES_API:
                line_items = [{
                    "name": line_items_summary,
                    "amount": int(multiplier * total.incl_tax),
                    "currency": total.currency,
                    "quantity": 1,
                }]
            else:
                line_items = [{
                    "price_data":  {
                        "product_data": {
                            "name": line_items_summary,
                        },
                        "currency": total.currency,
                        "unit_amount": int(multiplier * total.incl_tax),
                    },
                    "quantity": 1,
                }]
        else:
            line_items = []
            if not settings.STRIPE_USE_PRICES_API:
                for line_item in all_line_items:
                    line_items.append({
                        "name": line_item.title,
                        "amount": int(multiplier * line_item.price_incl_tax),
                        "currency": line_item.price_currency,
                        "quantity": line_item.quantity
                    })
            else:
                for line_item in all_line_items:
                    line_items.append({
                        "price_data":  {
                            "product_data": {
                                "name": line_item.title,
                            },
                            "currency": line_item.price_currency,
                            "unit_amount": int(multiplier * line_item.price_incl_tax),
                        },
                        "quantity": line_item.quantity,
                    })

        basket.freeze()
        session = stripe.checkout.Session.create(
            mode="payment",
            customer_email=customer_email,
            payment_method_types=['card'],
            line_items=line_items,
            metadata=metadata,
            success_url=settings.STRIPE_PAYMENT_SUCCESS_URL.format(basket.id),
            cancel_url=settings.STRIPE_PAYMENT_CANCEL_URL.format(basket.id),
            payment_intent_data={
                'capture_method': 'manual',
            },
        )
        return session

    def retrieve_payment_intent(self, pi):
        return stripe.PaymentIntent.retrieve(pi)

    def capture(self, order_number, **kwargs):
        """
        if capture is set to false in charge, the charge will only be pre-authorized
        one need to use capture to actually charge the customer
        """
        logger.info("Initiating payment capture for order '%s' via stripe" % (order_number))
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
            logger.info("payment for order '%s' (id:%s) was captured via stripe (stripe_ref:%s)" % (order.number, order.id, charge_id))
        except Source.DoesNotExist as e:
            logger.exception('Source Error for order: \'{}\''.format(order_number) )
            raise Exception("Capture Failure could not find payment source for Order %s" % order_number)
        except Order.DoesNotExist as e:
            logger.exception('Order Error for order: \'{}\''.format(order_number) )
            raise Exception("Capture Failure Order %s does not exist" % order_number)
