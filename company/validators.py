from rest_framework.serializers import ValidationError

from company.models import Company


def company_unique(number):
    if Company.objects.filter(number=number).exists():
        raise ValidationError('Already registered')
