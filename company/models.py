from directory_validators.constants import choices
from directory_validators import enrolment as shared_validators

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.utils.translation import ugettext_lazy as _

from api.model_utils import TimeStampedModel
from company import helpers


class Company(TimeStampedModel):

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
        upload_to=helpers.path_and_rename_logos,
        blank=True,
        null=True
    )
    name = models.CharField(max_length=255)
    number = models.CharField(
        max_length=8,
        validators=[shared_validators.company_number],
        unique=True
    )
    contact_details = JSONField(
        blank=True,
        null=True,
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
    date_of_creation = models.DateField(blank=True, null=True, default=None)
    is_published = models.BooleanField(default=False)
    verification_code = models.CharField(
        _('verification code'),
        max_length=255,
        blank=True,
        null=True,
        default=''
    )
    verified_with_code = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class CompanyCaseStudy(TimeStampedModel):
    title = models.CharField(
        max_length=100,
    )
    description = models.CharField(
        max_length=1000,
    )
    sector = models.CharField(
        choices=choices.COMPANY_CLASSIFICATIONS,
        max_length=100,
    )
    website = models.URLField(
        max_length=255, null=True, blank=True, default=''
    )
    year = models.CharField(max_length=4)
    keywords = models.TextField()
    image_one = models.FileField(
        null=True,
        blank=True,
        upload_to=helpers.path_and_rename_supplier_case_study,
    )
    image_two = models.FileField(
        null=True,
        blank=True,
        upload_to=helpers.path_and_rename_supplier_case_study,
    )
    image_three = models.FileField(
        null=True,
        blank=True,
        upload_to=helpers.path_and_rename_supplier_case_study,
    )
    video_one = models.FileField(
        null=True,
        blank=True,
        upload_to=helpers.path_and_rename_supplier_case_study,
    )
    testimonial = models.CharField(
        max_length=1000, null=True, blank=True, default=''
    )
    company = models.ForeignKey(Company, related_name='supplier_case_studies')

    def __str__(self):
        return self.title
