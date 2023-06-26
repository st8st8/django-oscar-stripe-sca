from django.conf import settings
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils import timezone
import stripe
from django.apps import apps
import logging

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


class Facade(object):
    def __init__(self):
        stripe.api_key = settings.STRIPE_SECRET_KEY

    @staticmethod
    def get_friendly_decline_message(error):
        return 'The transaction was declined by your bank - please check your bankcard details and try again'

    @staticmethod
    def get_friendly_error_message(error):
        return 'An error occurred when communicating with the payment gateway.'

    def begin(self, basket, total):
        multiplier = 1
        if total.currency.upper() in ZERO_DECIMAL_CURRENCIES:
            multiplier = 1
        else:
            multiplier = 100

        site = Site.objects.get_current()
        line_items_summary = ", ".join(["{0}x{1}".format(l.quantity, l.product.title) for l in basket.lines.all()])
        line_items = [{
                "name": line_items_summary,
                "amount": int(multiplier * total.incl_tax),
                "currency": total.currency,
                "quantity": 1,
        }]
        basket.freeze()
        session = stripe.checkout.Session.create(
            customer_email=basket.owner.email,
            payment_method_types=['card'],
            line_items=line_items,
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
