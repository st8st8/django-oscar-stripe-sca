from django.conf import settings

STRIPE_API_VERSION = getattr(settings, "STRIPE_API_VERSION", "2020-03-02")
STRIPE_SEND_RECEIPT = getattr(settings, "STRIPE_SEND_RECEIPT", True)
STRIPE_PUBLISHABLE_KEY = getattr(settings, "STRIPE_PUBLISHABLE_KEY", None)
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", None)
STRIPE_COMPRESS_TO_ONE_LINE_ITEM = getattr(
    settings, "STRIPE_COMPRESS_TO_ONE_LINE_ITEM", True
)
STRIPE_USE_PRICES_API = getattr(settings, "STRIPE_USE_PRICES_API", True)
STRIPE_RETURN_URL_BASE = getattr(
    settings, "STRIPE_RETURN_URL_BASE", "http://localhost/"
)
STRIPE_PAYMENT_SUCCESS_URL = "{0}{1}".format(
    STRIPE_RETURN_URL_BASE, "/checkout/preview-stripe/{0}/"
)
STRIPE_PAYMENT_CANCEL_URL = "{0}{1}".format(
    STRIPE_RETURN_URL_BASE, "/checkout/stripe-payment-cancel/{0}/"
)
STRIPE_LINE_ITEM_FORMAT_STRING = getattr(
    settings, "STRIPE_LINE_ITEM_FORMAT_STRING", "{0}: {1}"
)
