from django.db import models
from django.utils import timezone
from django.utils.timezone import now
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

    class Meta:
        ordering = ('-created', '-modified')

    def __str__(self):
        return self.company_email


class OwnershipInvite(TimeStampedModel):

    new_owner_email = models.EmailField(unique=True)
    company = models.ForeignKey(Company, related_name='suppliers')
    requestor = models.ForeignKey(User, related_name='users')
    accepted = models.BooleanField(default=False)
    accepted_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return 'Transferring {} to {}'.format(
            self.company.name,
            self.new_owner_email
        )

    def accept(self):
        self.accepted = True
        self.accepted_date = now()
        self.save()
