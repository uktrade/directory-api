from rest_framework import serializers

from company import models, validators


def ensure_string_value(instance, value):
    return value or ''


class CompanyCaseStudySerializer(serializers.ModelSerializer):

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

    validate_website = ensure_string_value
    validate_testimonial = ensure_string_value
    validate_testimonial_name = ensure_string_value
    validate_testimonial_job_title = ensure_string_value
    validate_testimonial_company = ensure_string_value
    validate_short_summary = ensure_string_value
    validate_image_one_caption = ensure_string_value
    validate_image_two_caption = ensure_string_value
    validate_image_three_caption = ensure_string_value


class CompanyCaseStudyWithCompanySerializer(CompanyCaseStudySerializer):

    class Meta(CompanyCaseStudySerializer.Meta):
        depth = 2


class CompanySerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)
    date_of_creation = serializers.DateField()
    sectors = serializers.JSONField(required=False)
    logo = serializers.ImageField(
        max_length=None, allow_empty_file=False, use_url=True, required=False
    )
    supplier_case_studies = CompanyCaseStudySerializer(
        many=True, required=False, read_only=True
    )
    contact_details = serializers.JSONField(required=False)

    class Meta:
        model = models.Company
        fields = (
            'date_of_creation',
            'description',
            'employees',
            'export_status',
            'id',
            'keywords',
            'logo',
            'name',
            'number',
            'revenue',
            'sectors',
            'supplier_case_studies',
            'website',
            'contact_details',
            'modified',
            'verified_with_code',
            'is_verification_letter_sent',
            'twitter_url',
            'facebook_url',
            'linkedin_url',
        )
        read_only_fields = ('modified',)

    validate_website = ensure_string_value
    validate_description = ensure_string_value
    validate_twitter_url = ensure_string_value
    validate_facebook_url = ensure_string_value
    validate_linkedin_url = ensure_string_value

    def validate_contact_details(self, value):
        if self.partial:
            contact_details = self.instance.contact_details or {}
            contact_details.update(value)
            return contact_details
        return value


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
