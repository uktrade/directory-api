from rest_framework import serializers

from directory_validators import company as shared_validators
from directory_validators.constants import choices

from django.conf import settings

from company import models, validators


class AllowedFormatImageField(serializers.ImageField):

    def to_internal_value(self, data):
        file = super().to_internal_value(data)

        if file.image.format.upper() not in settings.ALLOWED_IMAGE_FORMATS:
            raise serializers.ValidationError(
                "Invalid image format, allowed formats: {}".format(
                    ", ".join(settings.ALLOWED_IMAGE_FORMATS)
                )
            )

        return file


class CompanyCaseStudySerializer(serializers.ModelSerializer):

    image_one = AllowedFormatImageField(
        max_length=None, allow_empty_file=False, use_url=True, required=False
    )
    image_two = AllowedFormatImageField(
        max_length=None, allow_empty_file=False, use_url=True, required=False
    )
    image_three = AllowedFormatImageField(
        max_length=None, allow_empty_file=False, use_url=True, required=False
    )

    class Meta:
        model = models.CompanyCaseStudy
        fields = (
            'company',
            'description',
            'image_one',
            'image_one_caption',
            'image_three',
            'image_three_caption',
            'image_two',
            'image_two_caption',
            'keywords',
            'pk',
            'sector',
            'short_summary',
            'slug',
            'testimonial',
            'testimonial_company',
            'testimonial_job_title',
            'testimonial_name',
            'title',
            'video_one',
            'website',
        )
        read_only_fields = ('slug',)


class CompanyCaseStudyWithCompanySerializer(CompanyCaseStudySerializer):

    class Meta(CompanyCaseStudySerializer.Meta):
        depth = 2


class CompanySerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)
    date_of_creation = serializers.DateField()
    sectors = serializers.JSONField(required=False)
    logo = AllowedFormatImageField(
        max_length=None, allow_empty_file=False, use_url=True, required=False
    )
    supplier_case_studies = CompanyCaseStudySerializer(
        many=True, required=False, read_only=True
    )
    has_valid_address = serializers.SerializerMethodField()
    keywords = serializers.CharField(
        validators=[
            shared_validators.keywords_word_limit,
            shared_validators.keywords_special_characters
        ],
        required=False
    )

    class Meta:
        model = models.Company
        fields = (
            'address_line_1',
            'address_line_2',
            'country',
            'date_of_creation',
            'description',
            'email_address',
            'email_full_name',
            'employees',
            'export_status',
            'facebook_url',
            'has_valid_address',
            'id',
            'is_published',
            'is_verification_letter_sent',
            'keywords',
            'linkedin_url',
            'locality',
            'logo',
            'mobile_number',
            'modified',
            'name',
            'number',
            'po_box',
            'postal_code',
            'postal_full_name',
            'sectors',
            'slug',
            'summary',
            'supplier_case_studies',
            'twitter_url',
            'verified_with_code',
            'verified_with_preverified_enrolment',
            'website',
        )
        read_only_fields = ('modified', 'is_published', 'slug')

    def get_has_valid_address(self, obj):
        return obj.has_valid_address()


class CompanyNumberValidatorSerializer(serializers.Serializer):
    number = serializers.CharField(validators=[
        validators.company_unique,
    ])


class VerifyCompanyWithCodeSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate_code(self, value):
        if value != self.context['expected_code']:
            raise serializers.ValidationError(
                "Invalid company verification code"
            )


class CompanySearchSerializer(serializers.Serializer):
    term = serializers.CharField()
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    sector = serializers.ChoiceField(
        choices=choices.COMPANY_CLASSIFICATIONS,
        required=False,
    )
