from django.conf import settings

from .constants import PACKAGE_NAME


STRIPE_LOGGER_NAME = getattr(
    settings, "STRIPE_LOGGER_NAME", PACKAGE_NAME
)

STRIPE_FACADE_CLASS_PATH = getattr(
    settings, "STRIPE_FACADE_CLASS_PATH", f"{PACKAGE_NAME}.facade.Facade"
)

STRIPE_API_VERSION = getattr(
    settings, "STRIPE_API_VERSION", "2020-03-02"
)

STRIPE_PUBLISHABLE_KEY = getattr(
    settings, "STRIPE_PUBLISHABLE_KEY", None
)

STRIPE_SECRET_KEY = getattr(
    settings, "STRIPE_SECRET_KEY", None
)

STRIPE_RETURN_URL_BASE = getattr(
    settings, "STRIPE_RETURN_URL_BASE", "http://localhost/"
)

STRIPE_PAYMENT_SUCCESS_URL = getattr(
    settings, "STRIPE_PAYMENT_SUCCESS_URL", None  # lazy if missing
)

STRIPE_PAYMENT_CANCEL_URL = getattr(
    settings, "STRIPE_PAYMENT_CANCEL_URL", None  # lazy if missing
)

STRIPE_SEND_RECEIPT = getattr(
    settings, "STRIPE_SEND_RECEIPT", True
)

STRIPE_USE_PRICES_API = getattr(
    settings, "STRIPE_USE_PRICES_API", True
)

STRIPE_COMPRESS_TO_ONE_LINE_ITEM = getattr(
    settings, "STRIPE_COMPRESS_TO_ONE_LINE_ITEM", False
)

STRIPE_ENABLE_TAX_COMPUTATION = getattr(
    settings, "STRIPE_ENABLE_TAX_COMPUTATION", False
)

STRIPE_DEFAULT_PRODUCT_TAX_CODE = getattr(
    settings, "STRIPE_DEFAULT_PRODUCT_TAX_CODE", None
)

STRIPE_DEFAULT_SHIPPING_TAX_CODE = getattr(
    settings, "STRIPE_DEFAULT_SHIPPING_TAX_CODE", "txcd_92010001"
)
# See: https://docs.stripe.com/tax/tax-codes?tax_code=shipping



