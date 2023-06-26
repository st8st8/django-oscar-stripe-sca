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

 - STRIPE_SEND_RECEIPT: (True/False) - whether to send the payment receipt to the purchaser
 - STRIPE_CURRENCY: Three letter currency code for the transaction
 - STRIPE_PUBLISHABLE_KEY: Your key from Stripe
 - STRIPE_SECRET_KEY: Your secret key from Stripe
 - STRIPE_RETURN_URL_BASE: The common portion of the URL parts of the following two URLs.  Not used itself.
 - STRIPE_PAYMENT_SUCCESS_URL: The URL to which Stripe should redirect upon payment success.
 - STRIPE_PAYMENT_CANCEL_URL: The URL to which Stripe should redirect upon payment cancel.

Views
=====
Three urls are provided in apps.py. Three views are provided in the views.py file. 
 - StripeSCAPaymentDetailsView:  This sets up the variables which will be sent to Stripe and renders a templates which injects those variables and redirects to Stripe. Payment will be taken by Stripe as a "Charge" step.
 - StripeSCASuccessResponseView:  This is a form view that is loaded after a successful payment.  The "Place order" button is a form which ultimately tells Stripe to "capture" the payment.
 - StripeSCACancelResponseView:  This is the view that will be shown if the user cancels the payment for any reason.

The latter two views should be the views to which STRIPE_PAYMENT_SUCCESS_URL and STRIPE_PAYMENT_CANCEL_URL refer.

If you want to extend these views you can.  Extend Oscar's checkout app, add three new views to extend these ones, and overwrite the URLs in your checkout apps apps.py file.


TODO
====
 - The sandbox and the tests have not been updated yet.
 - The STRIPE_PAYMENT_SUCCESS_URL and STRIPE_PAYMENT_CANCEL_URL settings could probably be removed

