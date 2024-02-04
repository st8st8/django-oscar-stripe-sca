from django.conf import settings
from django.urls import reverse_lazy

STRIPE_SEND_RECEIPT = getattr(settings, "STRIPE_SEND_RECEIPT", True)
STRIPE_PUBLISHABLE_KEY = getattr(settings, "STRIPE_PUBLISHABLE_KEY", None)
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", None)
STRIPE_COMPRESS_TO_ONE_LINE_ITEM = getattr(settings, "STRIPE_COMPRESS_TO_ONE_LINE_ITEM", True)
STRIPE_USE_PRICES_API = getattr(settings, "STRIPE_USE_PRICES_API", True)
STRIPE_RETURN_URL_BASE = getattr(settings, "STRIPE_RETURN_URL_BASE", "http://localhost/")
STRIPE_PAYMENT_SUCCESS_URL = getattr(settings, "STRIPE_PAYMENT_SUCCESS_URL", "{0}{1}".format(settings.STRIPE_RETURN_URL_BASE, reverse_lazy("checkout:stripe-preview")))
STRIPE_PAYMENT_CANCEL_URL = getattr(settings, "STRIPE_PAYMENT_CANCEL_URL", "{0}{1}".format(settings.STRIPE_RETURN_URL_BASE, reverse_lazy("checkout:stripe-cancel")))