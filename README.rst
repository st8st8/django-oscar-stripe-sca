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
 - STRIPE_RETURN_URL_BASE: Not used itself.  It's just the common portion of the URL parts of....
 - STRIPE_PAYMENT_SUCCESS_URL: The URL to which Stripe should redirect upon payment success
 - STRIPE_PAYMENT_CANCEL_URL: The URL to which Stripe should redirect upon payment cancel.

Views
=====
Currently no urls.py file is provided. Three views are provided in the views.py file.  You can either point URLs to these in your urls.py file, or extend these views in your own checkout app.  This is the approach that I have used:


    class MyShopStripeSCAPaymentDetailsView(stripe_sca_views.StripeSCAPaymentDetailsView):
        pass

    class MyShopStripeSCASuccessResponseView(stripe_sca_views.StripeSCASuccessResponseView):
        pass

    class MyShopStripeSCACancelView(stripe_sca_views.StripeSCACancelResponseView):
        pass


The latter two views should be the views to which STRIPE_PAYMENT_SUCCESS_URL and STRIPE_PAYMENT_CANCEL_URL refer.

TODO
====

 - The sandbox and the tests have not been updated yet.
 - Remove all Python 2 artefacts


