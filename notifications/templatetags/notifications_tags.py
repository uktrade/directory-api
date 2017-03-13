from django import template
from django.conf import settings


register = template.Library()


@register.filter
def company_profile_url(company_number):
    return settings.FAS_COMPANY_PROFILE_URL.format(number=company_number)
