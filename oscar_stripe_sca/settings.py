from django.conf import settings
from django.urls import reverse_lazy

STRIPE_SEND_RECEIPT = getattr(settings, "STRIPE_SEND_RECEIPT", True)
STRIPE_CURRENCY = getattr(settings, "STRIPE_CURRENCY", "EUR")
STRIPE_PUBLISHABLE_KEY = getattr(settings, "STRIPE_PUBLISHABLE_KEY", None)
STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", None)
STRIPE_RETURN_URL_BASE = getattr(settings, "STRIPE_RETURN_URL_BASE", "http://localhost/")
STRIPE_PAYMENT_SUCCESS_URL = getattr(settings, "STRIPE_PAYMENT_SUCCESS_URL", "{0}{1}".format(settings.STRIPE_RETURN_URL_BASE, reverse_lazy("checkout:stripe-preview")))
STRIPE_PAYMENT_CANCEL_URL = getattr(settings, "STRIPE_PAYMENT_CANCEL_URL", "{0}{1}".format(settings.STRIPE_RETURN_URL_BASE, reverse_lazy("checkout:stripe-cancel")))