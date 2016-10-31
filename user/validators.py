from rest_framework.serializers import ValidationError

from user import models


def email_unique(email):
    if models.User.objects.filter(company_email=email).exists():
        raise ValidationError(
            'That email address has already been registered.'
        )
