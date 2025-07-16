import logging

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import RedirectView

from oscar.apps.checkout.views import PaymentDetailsView as CorePaymentDetailsView
from oscar.core.exceptions import ModuleNotFoundError
from oscar.core.loading import get_class, get_model

from . import settings
from .constants import (
    PACKAGE_NAME,
    PAYMENT_EVENT_PURCHASE,
    PAYMENT_METHOD_STRIPE,
)
from .loading import get_class_by_path


logger = logging.getLogger(settings.STRIPE_LOGGER_NAME)

Facade = get_class_by_path(settings.STRIPE_FACADE_CLASS_PATH)

SourceType = get_model("payment", "SourceType")
Source = get_model("payment", "Source")
Line = get_model("basket", "Line")
Basket = get_model("basket", "Basket")
Selector = get_class("partner.strategy", "Selector")
try:
    Applicator = get_class("offer.applicator", "Applicator")
except ModuleNotFoundError:
    # fallback for django-oscar<=1.1
    Applicator = get_class("offer.utils", "Applicator")


class StripeSCAPaymentDetailsView(CorePaymentDetailsView):
    template_name = f"{PACKAGE_NAME}/stripe_payment_details.html"

    def get_context_data(self, **kwargs):
        context_data = super().get_context_data(**kwargs)

        basket = context_data["basket"]
        total = context_data["order_total"]
        shipping_method = context_data["shipping_method"]
        customer_email = None
        try:
            customer_email = context_data["basket"].owner.email
        except AttributeError:
            checkout_data = self.request.session[
                self.checkout_session.SESSION_KEY
            ]
            customer_email = checkout_data["guest"]["email"]

        stripe_session = Facade().begin(
            customer_email=customer_email,
            basket=basket,
            total=total,
            shipping_method=shipping_method,
        )
        stripe_session_id = stripe_session.id
        stripe_payment_intent_id = stripe_session.payment_intent

        self.request.session["stripe_session_id"] = stripe_session_id
        self.request.session["stripe_payment_intent_id"] = stripe_payment_intent_id

        context_data.update({
            "stripe_publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
            "stripe_session_id": stripe_session_id
        })
        return context_data


class StripeSCASuccessResponseView(CorePaymentDetailsView):
    preview = True
    template_name_preview = f"{PACKAGE_NAME}/stripe_preview.html"

    @property
    def pre_conditions(self):
        return []

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(StripeSCASuccessResponseView, self).dispatch(
            request, *args, **kwargs
        )

    def get_context_data(self, **kwargs):
        ctx = super(StripeSCASuccessResponseView, self).get_context_data(**kwargs)
        if ctx["order_total"] is None:
            messages.error(
                self.request, "Your checkout session has expired, please try again"
            )
            raise PermissionDenied
        else:
            ctx["order_total_incl_tax_cents"] = (
                ctx["order_total"].incl_tax * 100
            ).to_integral_value()
        return ctx

    def handle_payment(self, order_number, order_total, **kwargs):
        pi = self.request.session["stripe_payment_intent_id"]
        intent = Facade().retrieve_payment_intent(pi)
        intent.capture()

        source_type, __ = SourceType.objects.get_or_create(name=PAYMENT_METHOD_STRIPE)
        source = Source(
            source_type=source_type,
            currency=order_total.currency,
            amount_allocated=order_total.incl_tax,
            amount_debited=order_total.incl_tax,
            reference=pi,
        )
        self.add_payment_source(source)

        self.add_payment_event(
            PAYMENT_EVENT_PURCHASE, order_total.incl_tax, reference=pi
        )

        del self.request.session["stripe_session_id"]
        del self.request.session["stripe_payment_intent_id"]

    def payment_description(self, order_number, total, **kwargs):
        return "Stripe payment for order {0} by {1}".format(
            order_number, self.request.user.get_full_name()
        )

    @staticmethod
    def payment_metadata(order_number, total, **kwargs):
        return {
            "order_number": order_number,
        }

    def load_frozen_basket(self, basket_id):
        # Lookup the frozen basket that this txn corresponds to
        try:
            basket = Basket.objects.get(id=basket_id, status=Basket.FROZEN)
        except Basket.DoesNotExist:
            return None

        # Assign strategy to basket instance
        if Selector:
            basket.strategy = Selector().strategy(self.request)

        # Re-apply any offers
        Applicator().apply(basket, self.request.user, request=self.request)

        return basket

    def get(self, request, *args, **kwargs):
        kwargs["basket"] = self.load_frozen_basket(kwargs["basket_id"])
        if not kwargs["basket"]:
            logger.warning(
                "Unable to load frozen basket with ID %s", kwargs["basket_id"]
            )
            messages.error(
                self.request,
                _("No basket was found that corresponds to your " "Stripe transaction"),
            )
            return HttpResponseRedirect(reverse("basket:summary"))
        return super(StripeSCASuccessResponseView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Place an order.
        """
        # Reload frozen basket which is specified in the URL
        basket = self.load_frozen_basket(kwargs["basket_id"])
        if not basket:
            messages.error(
                self.request,
                _("No basket was found that corresponds to your Stripe transaction"),
            )
            return HttpResponseRedirect(reverse("basket:summary"))

        submission = self.build_submission(basket=basket)
        return self.submit(**submission)


class StripeSCACancelResponseView(RedirectView):
    permanent = False

    def get(self, request, *args, **kwargs):
        basket = get_object_or_404(Basket, id=kwargs["basket_id"], status=Basket.FROZEN)
        basket.thaw()
        logger.info(
            "Payment cancelled (token %s) - basket #%s thawed",
            request.GET.get("token", "<no token>"),
            basket.id,
        )
        return super(StripeSCACancelResponseView, self).get(request, *args, **kwargs)

    def get_redirect_url(self, **kwargs):
        messages.error(self.request, _("Stripe transaction cancelled"))
        return reverse("basket:summary")
