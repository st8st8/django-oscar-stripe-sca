from oscar.apps.checkout.apps import CheckoutConfig
from oscar.core.loading import get_class
from django.urls import path


class StripeSCACheckoutConfig(CheckoutConfig):
    def ready(self):
        self.stripe_payment_details_view = get_class("oscar_stripe_sca.views", "StripeSCAPaymentDetailsView")
        self.stripe_success_view = get_class("oscar_stripe_sca.views", "StripeSCASuccessResponseView")
        self.stripe_cancel_view = get_class("oscar_stripe_sca.views", "StripeSCACancelResponseView")
        super().ready()

    def get_urls(self):
        urls = super(StripeSCACheckoutConfig, self).get_urls()
        urls += [
            path('payment-details-stripe/',
                self.stripe_payment_details_view.as_view(), name='stripe-payment-details'),
            path('preview-stripe/<int:basket_id>/',
                self.stripe_success_view.as_view(preview=True), name='stripe-preview'),
            path('payment-cancel/<int:basket_id>/',
                self.stripe_cancel_view.as_view(), name='stripe-cancel'),
        ]
        return urls
    

class MockStripeSCACheckoutConfig(StripeSCACheckoutConfig):
    """Checkout app config that wires in mock Stripe views for tests."""

    def ready(self):
        super().ready()
        from oscar_stripe_sca.testing import (
            MockStripePaymentDetailsView,
            MockStripeSuccessResponseView,
        )

        self.payment_details_view = MockStripePaymentDetailsView
        self.stripe_success_view = MockStripeSuccessResponseView
