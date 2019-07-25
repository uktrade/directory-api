import uuid

from directory_constants import choices, company_types
from directory_validators import enrolment as shared_validators
from directory_validators.company import no_html

from django.conf import settings
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _

from core.helpers import TimeStampedModel
from field_history.tracker import FieldHistoryTracker

from company import helpers


class Company(TimeStampedModel):
    company_type = models.CharField(
        max_length=15,
        choices=choices.COMPANY_TYPES,
        default=company_types.COMPANIES_HOUSE
    )
    summary = models.CharField(
        max_length=250,
        blank=True,
        default='',
        validators=[no_html],
    )
    description = models.TextField(
        blank=True,
        default='',
        validators=[no_html],
    )
    employees = models.CharField(
        max_length=20,
        choices=choices.EMPLOYEES,
        blank=True,
        default='',
    )
    export_destinations = JSONField(
        blank=True,
        default=[],
        help_text=(
            "Of the countries the project have prioritised,"
            "which does the company want to export to (whitelisted)"
        )
    )
    export_destinations_other = models.CharField(
        max_length=1000,
        blank=True,
        default='',
        help_text=(
            "Of the countries the project have not prioritised,"
            "which does the company want to export to (free text)."
        ),
        validators=[no_html],
    )
    expertise_industries = JSONField(
        blank=True,
        default=[],
        help_text=(
            "The industries that this company has expertise in,"
            "this allows searching and filtering for this selection"
        )
    )
    expertise_regions = JSONField(
        blank=True,
        default=[],
        help_text="The regions that this company has expertise in."
    )
    expertise_countries = JSONField(
        blank=True,
        default=[],
        help_text="The countries that this company has expertise in."
    )
    expertise_languages = JSONField(
        blank=True,
        default=[],
        help_text="The languages that this company has expertise in."
    )
    expertise_products_services = JSONField(
        blank=True,
        default={},
        help_text="The products and services the company has expertise in."
    )
    has_exported_before = models.NullBooleanField()
    is_exporting_goods = models.BooleanField(default=False)
    is_exporting_services = models.BooleanField(default=False)
    keywords = models.TextField(
        blank=True,
        default='',
        validators=[no_html],
    )
    logo = models.ImageField(
        upload_to=helpers.path_and_rename_logos,
        default='',
        blank=True,
    )
    name = models.CharField(
        max_length=255,
        validators=[no_html],
    )
    number = models.CharField(
        help_text=(
            'For companies registered in companies house this is their '
            'companies house number. For sole trader this is any randomly '
            'generated string.'
        ),
        max_length=8,
        validators=[
            shared_validators.company_number,
            no_html
        ],
        unique=True,
        null=True,
        blank=True,
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
    is_published_investment_support_directory = models.BooleanField(
        default=False,
        help_text=(
            'Companies that have a published profile on investment support.'
            'completeness - they must have description or summary, be '
            'verified, and have an email address.'
        )
    )

    is_published_find_a_supplier = models.BooleanField(
        default=False,
        help_text=(
            'Companies that have a published profile on FAS '
            'completeness - they must have description or summary, be '
            'verified, and have an email address.'
        )
    )
    date_published = models.DateField(null=True, blank=True)
    verification_code = models.CharField(
        _('verification code'),
        max_length=255,
        blank=True,
        default=helpers.generate_verification_code,
    )
    verified_with_preverified_enrolment = models.BooleanField(default=False)
    verified_with_code = models.BooleanField(default=False)
    verified_with_companies_house_oauth2 = models.BooleanField(default=False)
    is_verification_letter_sent = models.BooleanField(default=False)
    is_registration_letter_sent = models.BooleanField(default=False)
    date_registration_letter_sent = models.DateTimeField(
        null=True, blank=True
    )
    date_verification_letter_sent = models.DateTimeField(
        null=True, blank=True
    )
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
        validators=[no_html],
    )
    address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        default='',
        validators=[no_html],
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        default='',
        validators=[no_html],
    )
    locality = models.CharField(
        max_length=255,
        blank=True,
        default='',
        validators=[no_html],
    )
    country = models.CharField(
        max_length=255,
        blank=True,
        default='',
        validators=[no_html],
    )
    postal_code = models.CharField(
        max_length=255,
        blank=True,
        default='',
        validators=[no_html],
    )
    po_box = models.CharField(
        max_length=255,
        blank=True,
        default='',
        validators=[no_html],
    )
    email_address = models.EmailField(
        blank=True,
        default='',
    )
    email_full_name = models.CharField(
        max_length=200,
        blank=True,
        default='',
        validators=[no_html],
    )
    slug = models.SlugField()
    is_showcase_company = models.BooleanField(default=False)
    is_uk_isd_company = models.BooleanField(default=False)

    field_history = FieldHistoryTracker([
        'verified_with_preverified_enrolment',
        'verified_with_code',
        'verified_with_companies_house_oauth2',
    ])

    class Meta:
        verbose_name_plural = 'companies'

    def __str__(self):
        return self.name

    @property
    def is_publishable(self):
        has_contact = bool(self.email_address)
        has_synopsis = bool(self.description or self.summary)
        is_verified = self.is_verified
        return all([has_contact, has_synopsis, is_verified])

    @property
    def is_published(self):
        return any([
            self.is_published_investment_support_directory,
            self.is_published_find_a_supplier,
        ])

    @property
    def public_profile_url(self):
        return settings.FAS_COMPANY_PROFILE_URL.format(number=self.number)

    @property
    def is_verified(self):
        return any([
            self.verified_with_preverified_enrolment,
            self.verified_with_code,
            self.verified_with_companies_house_oauth2,
        ])

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
        validators=[no_html],
    )
    short_summary = models.CharField(
        max_length=200,
        blank=True,
        default='',
        validators=[no_html],
    )
    description = models.CharField(
        max_length=1000,
        validators=[no_html],
    )
    sector = models.CharField(
        choices=choices.INDUSTRIES,
        max_length=100,
    )
    website = models.URLField(
        max_length=255, blank=True, default=''
    )
    keywords = models.TextField(
        validators=[no_html]
    )
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
        max_length=200, blank=True, default='', validators=[no_html],
    )
    image_two_caption = models.CharField(
        max_length=200, blank=True, default='', validators=[no_html],
    )
    image_three_caption = models.CharField(
        max_length=200, blank=True, default='', validators=[no_html],
    )
    video_one = models.FileField(
        blank=True,
        default='',
        upload_to=helpers.path_and_rename_supplier_case_study,
    )
    testimonial = models.CharField(
        max_length=1000, blank=True, default='', validators=[no_html],
    )
    testimonial_name = models.CharField(
        max_length=255, blank=True, default='', validators=[no_html],
    )
    testimonial_job_title = models.CharField(
        max_length=255, blank=True, default='', validators=[no_html],
    )
    testimonial_company = models.CharField(
        max_length=255, blank=True, default='', validators=[no_html],
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


class OwnershipInvite(TimeStampedModel):

    uuid = models.UUIDField(default=uuid.uuid4)
    new_owner_email = models.EmailField(unique=True)
    company = models.ForeignKey(Company)
    requestor = models.ForeignKey('supplier.Supplier')
    accepted = models.BooleanField(default=False)
    accepted_date = models.DateTimeField(null=True, blank=True)

    @property
    def subject(self):
        return settings.OWNERSHIP_INVITE_SUBJECT.format(
            company_name=self.company.name
        )

    @property
    def recipient_email(self):
        return self.new_owner_email

    @property
    def invite_link(self):
        return settings.FAB_OWNERSHIP_URL.format(
            uuid=self.uuid
        )


class CollaboratorInvite(TimeStampedModel):

    uuid = models.UUIDField(default=uuid.uuid4)
    collaborator_email = models.EmailField(unique=True)
    company = models.ForeignKey(Company)
    requestor = models.ForeignKey('supplier.Supplier')
    accepted = models.BooleanField(default=False)
    accepted_date = models.DateTimeField(null=True, blank=True)

    @property
    def subject(self):
        return settings.COLLABORATOR_INVITE_SUBJECT.format(
            company_name=self.company.name
        )

    @property
    def recipient_email(self):
        return self.collaborator_email

    @property
    def invite_link(self):
        return settings.FAB_COLLABORATOR_URL.format(
            uuid=self.uuid
        )


class CollaboratorRequest(TimeStampedModel):
    collaborator_email = models.EmailField()
    company = models.ForeignKey(Company)

    class Meta:
        unique_together = ('collaborator_email', 'company')
