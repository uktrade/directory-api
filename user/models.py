from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from api.model_utils import TimeStampedModel
from company.models import Company


class User(TimeStampedModel):

    sso_id = models.PositiveIntegerField(
        _('sso user.sso_id'),
        unique=True,
    )
    name = models.CharField(
        _('name'),
        max_length=255,
        blank=True,
        null=True,  # serializer validation requires both null & default
        default='',
    )
    mobile_number = models.CharField(
        max_length=20,
        unique=True,
    )
    company = models.ForeignKey(
        Company, related_name='suppliers', null=True
    )

    company_email = models.EmailField(
        _('company email'),
        unique=True
    )
    company_email_confirmed = models.BooleanField(
        _('company email confirmed'),
        default=False,
        help_text=_(
            'Designates whether the user has confirmed company_email address.'
        ),
    )
    company_email_confirmation_code = models.CharField(
        _('company email confirmation code'),
        max_length=255,
        blank=True,
        null=True,
        default=''
    )

    referrer = models.CharField(
        _('referrer'),
        max_length=255,
        blank=True,
        null=True,
        default='',  # serializer validation requires both null & default
    )

    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now,
    )

    terms_agreed = models.BooleanField(
        _('terms_agreed'),
        default=False
    )

    class Meta:
        ordering = ('-created', '-modified')

    def __str__(self):
        return self.company_email
