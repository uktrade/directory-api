import http

from rest_framework.serializers import ValidationError

from company.models import Company
from company import helpers


def company_unique(number):
    if Company.objects.filter(number=number).exists():
        raise ValidationError('Already registered')


def company_active(number):
    response = helpers.get_companies_house_profile(number)
    if response.status_code == http.client.NOT_FOUND:
        raise ValidationError('Company not found. Please check the number.')
    if response.json()['company_status'] != 'active':
        raise ValidationError('Company not active.')
