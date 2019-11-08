from django.db import models
from django.utils import timezone

from core.helpers import TimeStampedModel
from company.models import Company

from directory_constants import choices, user_roles


# deprecated. use company.CompanyUser instead
class Supplier(TimeStampedModel):
    sso_id = models.PositiveIntegerField(verbose_name='sso user.sso_id', unique=True)
    name = models.CharField(verbose_name='name', max_length=255, blank=True, null=True, default='')
    company = models.ForeignKey(Company, related_name='suppliers', null=True, blank=True)
    company_email = models.EmailField('company email', unique=True)
    is_active = models.BooleanField(
        verbose_name='active',
        default=True,
        help_text=(
            'Designates whether this user should be treated as active. Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(verbose_name='date joined', default=timezone.now,)
    # deprecated in favour of company.models.Company.contact_details
    mobile_number = models.CharField(max_length=20, null=True, blank=True)
    unsubscribed = models.BooleanField(
        verbose_name='unsubscribed',
        default=False,
        help_text='Designates whether this user should receive notifications',
    )
    role = models.CharField(max_length=15, choices=choices.USER_ROLES, default=user_roles.EDITOR)

    @property
    def is_company_owner(self):
        return self.role == user_roles.ADMIN

    class Meta:
        ordering = ('-created', '-modified')

    def __str__(self):
        return self.company_email
