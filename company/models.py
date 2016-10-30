from directory_validators.constants import choices
from directory_validators import enrolment as shared_validators

from company.utils import path_and_rename

from django.db import models
from django.contrib.postgres.fields import JSONField


class Company(models.Model):

    # NOTE: For various reasons owing to how django handles empty values
    # in strings and how DRF serializers handle validation,
    # blank=True, null=True and default='' were necessary to keep
    # behaviour consistent between not specifying a field and
    # specifying it as None
    description = models.TextField(
        blank=True, null=True, default=''
    )
    employees = models.CharField(
        max_length=20,
        choices=choices.EMPLOYEES,
        blank=True,
        null=True,
        default=''
    )
    export_status = models.CharField(
        max_length=20,
        choices=choices.EXPORT_STATUSES,
        validators=[shared_validators.export_status_intention]
    )
    keywords = models.TextField(blank=True, null=True, default='')
    logo = models.FileField(
        upload_to=path_and_rename('company_logos'),
        blank=True,
        null=True
    )
    name = models.CharField(max_length=255)
    number = models.CharField(
        max_length=8,
        validators=[shared_validators.company_number],
        unique=True
    )
    revenue = models.DecimalField(
        max_digits=13,
        decimal_places=2,
        blank=True,
        null=True,
    )
    sectors = JSONField(
        blank=True,
        null=True,
    )
    website = models.URLField(
        max_length=255, blank=True, null=True,
        default=''
    )

    def __str__(self):
        return self.name
