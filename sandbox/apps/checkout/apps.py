from django.urls import re_path
from oscar.apps.checkout.apps import CheckoutConfig


class StripeSCASandboxCheckoutConfig(CheckoutConfig):
    name = "apps.checkout"

    def ready(self):
        super().ready()
        from oscar_stripe_sca import views as stripe_sca_views

        self.payment_details_view = stripe_sca_views.StripeSCAPaymentDetailsView
        self.stripe_success_view = stripe_sca_views.StripeSCASuccessResponseView
        self.stripe_cancel_view = stripe_sca_views.StripeSCACancelResponseView

    def get_urls(self):
        urls = super().get_urls()
        urls += [
            re_path(
                r"preview-stripe/(?P<basket_id>\d+)/$",
                self.stripe_success_view.as_view(preview=True),
                name="stripe-preview",
            ),
            re_path(
                r"stripe-payment-cancel/(?P<basket_id>\d+)/$",
                self.stripe_cancel_view.as_view(),
                name="stripe-cancel",
            ),
        ]
        return urls
