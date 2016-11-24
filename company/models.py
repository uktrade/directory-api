from directory_validators.constants import choices
from directory_validators import company as shared_company_validators
from directory_validators import enrolment as shared_enrolment_validators

from django.db import models
from django.contrib.postgres.fields import JSONField

from company import helpers


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
        validators=[shared_enrolment_validators.export_status_intention]
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
        validators=[shared_enrolment_validators.company_number],
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
    date_of_creation = models.DateField(blank=True, null=True, default=None)

    def __str__(self):
        return self.name


class SupplierCaseStudy(models.Model):
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
        max_length=255, null=True, blank=True,  default=''
    )
    year = models.CharField(max_length=4)
    keywords = models.TextField(blank=True, null=True, default='')
    image_one = models.FileField(
        null=True,
        blank=True,
        default='',
        upload_to=helpers.path_and_rename_supplier_case_study,
        validators=[shared_company_validators.case_study_image_filesize],
    )
    image_two = models.FileField(
        null=True,
        blank=True,
        default='',
        upload_to=helpers.path_and_rename_supplier_case_study,
        validators=[shared_company_validators.case_study_image_filesize],
    )
    image_three = models.FileField(
        null=True,
        blank=True,
        default='',
        upload_to=helpers.path_and_rename_supplier_case_study,
        validators=[shared_company_validators.case_study_image_filesize],
    )
    video_one = models.FileField(
        null=True,
        blank=True,
        default='',
        upload_to=helpers.path_and_rename_supplier_case_study,
        validators=[shared_company_validators.case_study_video_filesize],
    )
    testimonial = models.CharField(
        max_length=1000, null=True, blank=True, default=''
    )
    company = models.ForeignKey(Company, related_name='supplier_case_studies')

    def __str__(self):
        return self.title
