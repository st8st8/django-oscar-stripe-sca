# myproject/promotions/app.py
from oscar.apps.checkout.app import CheckoutApplication
from . import views
from django.conf.urls import url


class StripeSCACheckoutApplication(CheckoutApplication):
    stripe_payment_details_view = views.StripeSCAPaymentDetailsView
    stripe_success_view = views.StripeSCASuccessResponseView
    stripe_cancel_view = views.StripeSCACancelResponseView

    def get_urls(self):
        urls = super(StripeSCACheckoutApplication, self).get_urls()
        urls += [
            url(r'payment-details-stripe/$',
                self.stripe_payment_details_view.as_view(), name='stripe-payment-details'),
            url(r'preview-stripe/(?P<basket_id>\d+)/$',
                self.stripe_success_view.as_view(preview=True), name='stripe-preview'),
            url(r'payment-cancel/(?P<basket_id>\d+)/$',
                self.stripe_cancel_view.as_view(), name='stripe-cancel'),
        ]
        return urls


application = StripeSCACheckoutApplication()
