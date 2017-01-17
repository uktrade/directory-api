from django.conf import settings

from rest_framework import serializers

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
            'image_three',
            'image_two',
            'keywords',
            'pk',
            'sector',
            'testimonial',
            'testimonial_name',
            'testimonial_job_title',
            'testimonial_company',
            'title',
            'video_one',
            'website',
            'short_summary',
            'image_one_caption',
            'image_two_caption',
            'image_three_caption',
        )


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

    class Meta:
        model = models.Company
        fields = (
            'date_of_creation',
            'description',
            'summary',
            'employees',
            'export_status',
            'id',
            'keywords',
            'logo',
            'name',
            'number',
            'sectors',
            'supplier_case_studies',
            'website',
            'modified',
            'verified_with_code',
            'is_verification_letter_sent',
            'is_published',
            'twitter_url',
            'facebook_url',
            'linkedin_url',
            'postal_full_name',
            'address_line_1',
            'address_line_2',
            'locality',
            'country',
            'postal_code',
            'po_box',
            'mobile_number',
            'email_address',
            'email_full_name',
            'has_valid_address',
        )
        read_only_fields = ('modified', 'is_published')

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
