from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from api.model_utils import TimeStampedModel
from company.models import Company


class Supplier(TimeStampedModel):
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
    company = models.ForeignKey(
        Company, related_name='suppliers', null=True
    )
    company_email = models.EmailField(
        _('company email'),
        unique=True
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
    # deprecated in favour of company.models.Company.contact_details
    mobile_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True,
    )
    unsubscribed = models.BooleanField(
        _('unsubscribed'),
        default=False,
        help_text=_(
            'Designates whether this user should receive notifications'
        ),
    )
    is_company_owner = models.BooleanField(default=False)
    govuk_verify_address = models.CharField(
        null=True,
        blank=True,
        help_text="For security purposes. Their address when they verified.",
        max_length=2000,
    )

    class Meta:
        ordering = ('-created', '-modified')

    def __str__(self):
        return self.company_email
