from rest_framework import serializers

from company import models, validators


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
            'source_name',
            'source_job_title',
            'source_company',
            'title',
            'video_one',
            'website',
            'year',
        )

    def validate_website(self, value):
        return value or ''

    def validate_testimonial(self, value):
        return value or ''

    def validate_source_name(self, value):
        return value or ''

    def validate_source_job_title(self, value):
        return value or ''

    def validate_source_company(self, value):
        return value or ''


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
        )
        read_only_fields = ('modified',)

    def validate_website(self, value):
        return value or ''

    def validate_description(self, value):
        return value or ''

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
