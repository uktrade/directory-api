from company.models import CompanyUser


def total_registered_company_users():
    # We're using the Number & Secondary Stat widget (and json format)
    # https://developer-custom.geckoboard.com/#number-and-secondary-stat
    return {"item": [{"value": CompanyUser.objects.count(), "text": "Total registered company users"}]}
