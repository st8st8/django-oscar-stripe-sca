from django import forms


class StripeTokenForm(forms.Form):
    stripeToken = forms.CharField(widget=forms.HiddenInput())
