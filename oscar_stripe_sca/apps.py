from oscar.apps.checkout.apps import CheckoutConfig
from oscar.core.loading import get_class
from django.urls import path


class StripeSCACheckoutConfig(CheckoutConfig):
    def ready(self):
        stripe_payment_details_view = get_class(
            "oscar_stripe_sca.views", "StripeSCAPaymentDetailsView"
        )
        stripe_success_view = get_class(
            "oscar_stripe_sca.views", "StripeSCASuccessResponseView"
        )
        stripe_cancel_view = get_class(
            "oscar_stripe_sca.views", "StripeSCACancelResponseView"
        )
        super().ready()

    def get_urls(self):
        urls = super(StripeSCACheckoutConfig, self).get_urls()
        urls += [
            path(
                "payment-details-stripe/",
                self.stripe_payment_details_view.as_view(),
                name="stripe-payment-details",
            ),
            path(
                "preview-stripe/<int:basket_id>/",
                self.stripe_success_view.as_view(preview=True),
                name="stripe-preview",
            ),
            path(
                "payment-cancel/<int:basket_id>/",
                self.stripe_cancel_view.as_view(),
                name="stripe-cancel",
            ),
        ]
        return urls
