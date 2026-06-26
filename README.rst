===================================
Stripe integration for django-oscar
===================================

pip3 install django-oscar-stripe-sca

This is a framework for using Stripe Checkout with a view for being SCA compliant for payments
in Europe after September 2019.  Requires the Python Stripe API (2.27), django 2 and above, django-oscar 2 and above. 
Based in part on django-oscar-stripe and django-oscar-paypal.

Useful information:

* `Stripe's Python API`_

.. _`Stripe's Python API`: https://stripe.com/docs/libraries

Contributing
============

Please do.  Let me know.

Settings
========
Settings are described in the settings.py file:

 - STRIPE_SEND_RECEIPT: (True/False) - whether to send the payment receipt to the purchaser.
 - STRIPE_PUBLISHABLE_KEY: Your key from Stripe. `pk_live_...` or `pk_test_...`
 - STRIPE_SECRET_KEY: Your secret key from Stripe. `sk_live_...` or `sk_test_...`
 - STRIPE_COMPRESS_TO_ONE_LINE_ITEM (default True): If True, send the order to stripe as one combined line item, instead of one for each product.
 - STRIPE_USE_PRICES_API (default True): Use Stripe's Prices API to send line items, rather than the defunct line_item object.
   (See https://stripe.com/docs/payments/checkout/migrating-prices).
 - STRIPE_RETURN_URL_BASE: The common portion of the URL parts of the following two URLs.  Not used itself.
 - STRIPE_PAYMENT_SUCCESS_URL: The URL to which Stripe should redirect upon payment success.
 - STRIPE_PAYMENT_CANCEL_URL: The URL to which Stripe should redirect upon payment cancel.

Session
-------

The browser can forget the session when handing over to Stripe.
Make sure to [configure your session](https://docs.djangoproject.com/en/5.2/topics/http/sessions/). E.g. `cookie-based`

Also, do not expire the session when the checkout replaces the shop:

```python
# settings.py
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
```

API Key
-------

We recommend using a [Restricted API Key](https://docs.stripe.com/keys/restricted-api-keys) with the following limited access to the account:

|      Resource     | Permission |
| ----------------- | ---------- |
| Checkout Sessions | Write      |
| Payment Intents   | Write      |

Views
=====
Three urls are provided in apps.py. Three views are provided in the views.py file. 
 - StripeSCAPaymentDetailsView:  This sets up the variables which will be sent to Stripe and renders a templates which injects those variables and redirects to Stripe. Payment will be taken by Stripe as a "Charge" step.
 - StripeSCASuccessResponseView:  This is a form view that is loaded after a successful payment.  The "Place order" button is a form which ultimately tells Stripe to "capture" the payment.
 - StripeSCACancelResponseView:  This is the view that will be shown if the user cancels the payment for any reason.

The latter two views should be the views to which STRIPE_PAYMENT_SUCCESS_URL and STRIPE_PAYMENT_CANCEL_URL refer.

If you want to extend these views you can.  Extend Oscar's checkout app, add three new views to extend these ones, and overwrite the URLs in your checkout apps apps.py file.

=======================================================
Sandbox for the Stripe SCA integration for django-oscar
=======================================================

To get started with the sandbox (on Windows):

Create a venv.

.. code-block::

    >python -m venv .\venv


Activate the venv.

.. code-block::

    >.\venv\Scripts\activate

Install the dependencies, then Oscar Stripe SCA

.. code-block::

    >pip install -r requirements.txt
    >pip install .


Create a file called "settings_local.py" next to "settings.py" and add the following three keys to override the examples given in "settings.py".  These will be the values for your shop and site integration.

.. code-block::

	STRIPE_PUBLISHABLE_KEY = "XXX"
 	STRIPE_SECRET_KEY = "YYY"
 	STRIPE_RETURN_URL_BASE = "https://www.zzz.com"

Run the migrations and start the server:

.. code-block::

    >cd sandbox
    >python manage.py migrate
    >python manage.py runserver

Testing without a Stripe account
=================================

``oscar_stripe_sca.testing`` provides drop-in mock views so that your
integration and feature tests never make real Stripe API calls.

Wiring in the mock config
--------------------------

Replace the real app config with the mock one in your test settings:

.. code-block:: python

    INSTALLED_APPS[
        INSTALLED_APPS.index("oscar_stripe_sca.apps.StripeSCACheckoutConfig")
    ] = "oscar_stripe_sca.apps.MockStripeSCACheckoutConfig"

This must happen before Django's app registry is initialised (i.e. in your settings module).

Controlling accept / cancel per test
--------------------------------------

The mock payment view reads ``settings.STRIPE_TESTING_OUTCOME`` on every
request, so you can flip it between test cases without restarting Django.

Add a default in your test settings:

.. code-block:: python

    STRIPE_TESTING_OUTCOME = "accept"  # or "cancel"

**pytest** — use the ``settings`` fixture from ``pytest-django``:

.. code-block:: python

    import pytest

    @pytest.mark.django_db
    def test_cancel(client, settings):
        settings.STRIPE_TESTING_OUTCOME = "cancel"
        # … drive checkout via the test client …

**behave** — override per scenario using tags in ``environment.py``:

.. code-block:: python

    # features/environment.py
    from django.conf import settings

    def before_scenario(context, scenario):
        settings.STRIPE_TESTING_OUTCOME = (
            "cancel" if "payment_cancel" in scenario.tags else "accept"
        )

Example behave feature test
-----------------------------

.. code-block:: gherkin

    Scenario: A logged-in user completes a purchase.
      ...
       Then I see "Your order has been placed"
    @payment_cancel
    Scenario: A logged-in user cancels payment.
      ...
       Then I see "Stripe transaction cancelled"

TODO
====
 - The tests have not been updated yet.
 - The STRIPE_PAYMENT_SUCCESS_URL and STRIPE_PAYMENT_CANCEL_URL settings could probably be removed

