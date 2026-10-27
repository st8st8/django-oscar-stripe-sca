import os

# Django settings for oscar project.
PROJECT_DIR = os.path.dirname(__file__)
location = lambda x: os.path.join(os.path.dirname(os.path.realpath(__file__)), x)

DEBUG = True
TEMPLATE_DEBUG = True
SQL_DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = os.path.join(PROJECT_DIR, "emails")

MANAGERS = ADMINS

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",  # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        "NAME": location("db.sqlite"),  # Or path to database file if using sqlite3.
        "ATOMIC_REQUESTS": True,
        "USER": "",  # Not used with sqlite3.
        "PASSWORD": "",  # Not used with sqlite3.
        "HOST": "",  # Set to empty string for localhost. Not used with sqlite3.
        "PORT": "",  # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = "Europe/London"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "en-us"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = location("public/media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = "/media/"

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
# ADMIN_MEDIA_PREFIX = '/media/admin/'

STATIC_URL = "/static/"
STATICFILES_DIRS = (location("static/"),)
STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = "!8(8ijbn^rd%y%ckok%ju_tce+g)iv09vog*ut#9^5-9uc&rhs"


MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.contrib.flatpages.middleware.FlatpageFallbackMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "oscar.apps.basket.middleware.BasketMiddleware",
]

DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

INTERNAL_IPS = ("127.0.0.1",)

ROOT_URLCONF = "urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            os.path.join(PROJECT_DIR, "templates"),
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.request",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "django.contrib.messages.context_processors.messages",
                # Oscar specific
                "oscar.apps.search.context_processors.search_form",
                "oscar.apps.checkout.context_processors.checkout",
                "oscar.apps.communication.notifications.context_processors.notifications",
                "oscar.core.context_processors.metadata",
            ]
        },
    }
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
        },
        "simple": {"format": "%(levelname)s %(message)s"},
    },
    "handlers": {
        "null": {
            "level": "DEBUG",
            "class": "logging.NullHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "oscar_stripe_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": os.path.join(PROJECT_DIR, "logs", "oscar_stripe_sca.log"),
            "formatter": "verbose",
        },
        "mail_admins": {
            "level": "ERROR",
            "class": "django.utils.log.AdminEmailHandler",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["null"],
            "propagate": True,
            "level": "INFO",
        },
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": False,
        },
        "oscar.checkout": {
            "handlers": ["console"],
            "propagate": True,
            "level": "INFO",
        },
        "django.db.backends": {
            "handlers": ["null"],
            "propagate": False,
            "level": "DEBUG",
        },
        "oscar_stripe_sca": {
            "handlers": ["console", "oscar_stripe_file"],
            "propagate": True,
            "level": "DEBUG",
        },
    },
}


INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.admin",
    "django.contrib.flatpages",
    "django.contrib.staticfiles",
    "widget_tweaks",
    "django_tables2",
    "sorl.thumbnail",
    "oscar.config.Shop",
    "oscar.apps.address.apps.AddressConfig",
    "apps.checkout.apps.StripeSCASandboxCheckoutConfig",
    "oscar.apps.dashboard.apps.DashboardConfig",
    "oscar.apps.partner.apps.PartnerConfig",
    "oscar.apps.basket.apps.BasketConfig",
    "oscar.apps.order.apps.OrderConfig",
    "oscar.apps.customer.apps.CustomerConfig",
    "oscar.apps.shipping.apps.ShippingConfig",
    "oscar.apps.dashboard.reports.apps.ReportsDashboardConfig",
    "oscar.apps.analytics.apps.AnalyticsConfig",
    "oscar.apps.catalogue.apps.CatalogueConfig",
    "oscar.apps.catalogue.reviews.apps.CatalogueReviewsConfig",
    "oscar.apps.communication.apps.CommunicationConfig",
    "oscar.apps.payment.apps.PaymentConfig",
    "oscar.apps.offer.apps.OfferConfig",
    "oscar.apps.search.apps.SearchConfig",
    "oscar.apps.voucher.apps.VoucherConfig",
    "oscar.apps.wishlists.apps.WishlistsConfig",
    "oscar.apps.dashboard.users.apps.UsersDashboardConfig",
    "oscar.apps.dashboard.orders.apps.OrdersDashboardConfig",
    "oscar.apps.dashboard.catalogue.apps.CatalogueDashboardConfig",
    "oscar.apps.dashboard.offers.apps.OffersDashboardConfig",
    "oscar.apps.dashboard.partners.apps.PartnersDashboardConfig",
    "oscar.apps.dashboard.pages.apps.PagesDashboardConfig",
    "oscar.apps.dashboard.ranges.apps.RangesDashboardConfig",
    "oscar.apps.dashboard.reviews.apps.ReviewsDashboardConfig",
    "oscar.apps.dashboard.vouchers.apps.VouchersDashboardConfig",
    "oscar.apps.dashboard.communications.apps.CommunicationsDashboardConfig",
    "oscar.apps.dashboard.shipping.apps.ShippingDashboardConfig",
    "oscar_stripe_sca",
]

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "oscar.apps.customer.auth_backends.EmailBackend",
)

LOGIN_REDIRECT_URL = "/accounts/"
APPEND_SLASH = True

HAYSTACK_CONNECTIONS = {
    "default": {
        "ENGINE": "haystack.backends.simple_backend.SimpleEngine",
    },
}

# =================
# Oscar settings
# =================
from oscar.defaults import *

OSCAR_ALLOW_ANON_CHECKOUT = True


# =================
# Stripe settings
# =================
STRIPE_COMPRESS_TO_ONE_LINE_ITEM = False
STRIPE_USE_PRICES_API = True

# Override these three.  I suggest creating a file called "settings_local.py", and adding the settings there.
# This file is .gitignore-d so this will avoid your stripe keys going into git.
STRIPE_PUBLISHABLE_KEY = "YOUR-STRIPE-PUBLISHABLE-KEY"
STRIPE_SECRET_KEY = "YOUR-STRIPE-SECRET-KEY"
STRIPE_RETURN_URL_BASE = "https://www.example.com/"

# If you don't want to use a settings_local.py, comment or remove this line.
from settings_local import *

STRIPE_PAYMENT_SUCCESS_URL = "{0}{1}".format(
    STRIPE_RETURN_URL_BASE, "/checkout/preview-stripe/{0}/"
)
STRIPE_PAYMENT_CANCEL_URL = "{0}{1}".format(
    STRIPE_RETURN_URL_BASE, "/checkout/stripe-payment-cancel/{0}/"
)
