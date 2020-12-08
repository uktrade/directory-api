from rest_framework.serializers import ValidationError

from company.models import Company

COMPANY_NOT_UNIQUE_MESSAGE = 'Already registered.'


def company_unique(number):
    if Company.objects.filter(number=number).exists():
        raise ValidationError(COMPANY_NOT_UNIQUE_MESSAGE)
