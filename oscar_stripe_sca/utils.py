from datetime import datetime


def get_stripe_api_version_as_date(stripe):
    return datetime.strptime(stripe.api_version, "%Y-%m-%d")
