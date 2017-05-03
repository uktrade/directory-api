from directory_validators.constants import choices
from directory_validators import enrolment as shared_validators

from django.db import models
from django.contrib.postgres.fields import JSONField
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from api.model_utils import TimeStampedModel
from company import helpers, search


class Company(TimeStampedModel):
    to_doc_type = search.company_model_to_doc_type
    summary = models.CharField(
        max_length=250,
        blank=True,
        default=''
    )
    description = models.TextField(
        blank=True,
        default='',
    )
    employees = models.CharField(
        max_length=20,
        choices=choices.EMPLOYEES,
        blank=True,
        default=''
    )
    export_status = models.CharField(
        max_length=20,
        choices=choices.EXPORT_STATUSES,
        validators=[shared_validators.export_status_intention]
    )
    keywords = models.TextField(
        blank=True,
        default='',
    )
    logo = models.ImageField(
        upload_to=helpers.path_and_rename_logos,
        default='',
        blank=True,
    )
    name = models.CharField(max_length=255)
    number = models.CharField(
        max_length=8,
        validators=[shared_validators.company_number],
        unique=True
    )
    sectors = JSONField(
        blank=True,
        default=[],
    )
    website = models.URLField(
        max_length=255,
        blank=True,
        default=''
    )
    date_of_creation = models.DateField(
        blank=True,
        null=True,
    )
    is_published = models.BooleanField(
        default=False,
        help_text=(
            'Companies are automatically published based on profile '
            'completeness - they must have description or summary, be '
            'verified, and have an email address.'
        )
    )
    date_published = models.DateField(null=True)
    verification_code = models.CharField(
        _('verification code'),
        max_length=255,
        blank=True,
        default=helpers.generate_verification_code,
    )
    verified_with_code = models.BooleanField(default=False)
    is_verification_letter_sent = models.BooleanField(default=False)
    date_verification_letter_sent = models.DateTimeField(null=True)
    # social links
    twitter_url = models.URLField(
        max_length=255,
        blank=True,
        default=''
    )
    facebook_url = models.URLField(
        max_length=255,
        blank=True,
        default=''
    )
    linkedin_url = models.URLField(
        max_length=255,
        blank=True,
        default='',
    )
    # contact details
    mobile_number = models.CharField(
        blank=True,
        default='',
        max_length=100,
    )
    postal_full_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    locality = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    country = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    postal_code = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    po_box = models.CharField(
        max_length=255,
        blank=True,
        default='',
    )
    email_address = models.EmailField(
        blank=True,
        default='',
    )
    email_full_name = models.CharField(
        max_length=200,
        blank=True,
        default='',
    )
    slug = models.SlugField()

    class Meta:
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name

    def has_valid_address(self):
        required_address_fields = [
            'postal_full_name',
            'address_line_1',
            'postal_code',
        ]
        return all(getattr(self, field) for field in required_address_fields)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)[:50]
        return super().save(*args, **kwargs)


class CompanyCaseStudy(TimeStampedModel):
    title = models.CharField(
        max_length=100,
    )
    short_summary = models.CharField(
        max_length=200, blank=True, default=''
    )
    description = models.CharField(
        max_length=1000,
    )
    sector = models.CharField(
        choices=choices.COMPANY_CLASSIFICATIONS,
        max_length=100,
    )
    website = models.URLField(
        max_length=255, blank=True, default=''
    )
    keywords = models.TextField()
    image_one = models.ImageField(
        upload_to=helpers.path_and_rename_supplier_case_study,
        blank=True,
        default='',
    )
    image_two = models.ImageField(
        upload_to=helpers.path_and_rename_supplier_case_study,
        blank=True,
        default='',
    )
    image_three = models.ImageField(
        upload_to=helpers.path_and_rename_supplier_case_study,
        blank=True,
        default='',
    )
    image_one_caption = models.CharField(
        max_length=200, blank=True, default=''
    )
    image_two_caption = models.CharField(
        max_length=200, blank=True, default=''
    )
    image_three_caption = models.CharField(
        max_length=200, blank=True, default=''
    )
    video_one = models.FileField(
        blank=True,
        default='',
        upload_to=helpers.path_and_rename_supplier_case_study,
    )
    testimonial = models.CharField(
        max_length=1000, blank=True, default=''
    )
    testimonial_name = models.CharField(
        max_length=255, blank=True, default=''
    )
    testimonial_job_title = models.CharField(
        max_length=255, blank=True, default=''
    )
    testimonial_company = models.CharField(
        max_length=255, blank=True, default=''
    )
    company = models.ForeignKey(Company, related_name='supplier_case_studies')

    slug = models.SlugField()

    class Meta:
        verbose_name_plural = 'company case studies'

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)[:50]
        return super().save(*args, **kwargs)
