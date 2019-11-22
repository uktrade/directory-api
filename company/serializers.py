from django.utils.timezone import now
from rest_framework import serializers

import directory_validators.string
from directory_constants import choices, user_roles

from django.conf import settings
from django.http import QueryDict

from company import models, validators
from core.helpers import CompaniesHouseClient


class AllowedFormatImageField(serializers.ImageField):

    def to_internal_value(self, data):
        file = super().to_internal_value(data)
        if file.image.format.upper() not in settings.ALLOWED_IMAGE_FORMATS:
            allowed = ", ".join(settings.ALLOWED_IMAGE_FORMATS)
            raise serializers.ValidationError(f"Invalid image format, allowed formats: {allowed}")
        return file


class CompanyCaseStudySerializer(serializers.ModelSerializer):
    image_one = AllowedFormatImageField(max_length=None, allow_empty_file=False, use_url=True, required=False)
    image_two = AllowedFormatImageField(max_length=None, allow_empty_file=False, use_url=True, required=False)
    image_three = AllowedFormatImageField(max_length=None, allow_empty_file=False, use_url=True, required=False)

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

    def to_internal_value(self, data):
        if isinstance(data, QueryDict):
            data = data.dict()
        data['company'] = self.context['request'].user.company.pk
        return super().to_internal_value(data)


class CompanyCaseStudyWithCompanySerializer(CompanyCaseStudySerializer):

    class Meta(CompanyCaseStudySerializer.Meta):
        depth = 2


class CompanySerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)
    date_of_creation = serializers.DateField()
    sectors = serializers.JSONField(required=False)
    logo = AllowedFormatImageField(max_length=None, allow_empty_file=False, use_url=True, required=False)
    supplier_case_studies = CompanyCaseStudySerializer(many=True, required=False, read_only=True)
    has_valid_address = serializers.SerializerMethodField()
    keywords = serializers.CharField(
        validators=[directory_validators.string.word_limit(10), directory_validators.string.no_special_characters],
        required=False
    )

    class Meta:
        model = models.Company
        fields = (
            'address_line_1',
            'address_line_2',
            'company_type',
            'country',
            'created',
            'date_of_creation',
            'description',
            'email_address',
            'email_full_name',
            'employees',
            'facebook_url',
            'has_exported_before',
            'has_valid_address',
            'id',
            'is_exporting_goods',
            'is_exporting_services',
            'is_published',
            'is_publishable',
            'is_published_investment_support_directory',
            'is_published_find_a_supplier',
            'is_registration_letter_sent',
            'is_verification_letter_sent',
            'is_identity_check_message_sent',
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
            'website',
            'verified_with_code',
            'verified_with_preverified_enrolment',
            'verified_with_companies_house_oauth2',
            'verified_with_identity_check',
            'is_verified',
            'export_destinations',
            'export_destinations_other',
            'is_uk_isd_company',
            'expertise_industries',
            'expertise_regions',
            'expertise_countries',
            'expertise_languages',
            'expertise_products_services',
        )
        extra_kwargs = {
            'export_status': {'required': False},
            'has_exported_before': {'required': False},
            'modified': {'read_only': True},
            'slug': {'read_only': True},
        }

    def get_has_valid_address(self, obj):
        return obj.has_valid_address()


class CompanyNumberValidatorSerializer(serializers.Serializer):
    number = serializers.CharField(validators=[validators.company_unique])


class VerifyCompanyWithCodeSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate_code(self, value):
        if value != self.context['expected_code']:
            raise serializers.ValidationError('Invalid company verification code')


class SearchSerializer(serializers.Serializer):

    OPTIONAL_FILTERS = [
        'term',
        'expertise_industries',
        'expertise_regions',
        'expertise_countries',
        'expertise_languages',
        'expertise_products_services_labels',
        'sectors',
    ]

    MESSAGE_MISSING_QUERY = 'Please specify a term or filter'

    term = serializers.CharField(required=False)
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    sectors = serializers.MultipleChoiceField(choices=choices.INDUSTRIES, required=False)
    expertise_industries = serializers.MultipleChoiceField(choices=choices.INDUSTRIES, required=False)
    expertise_regions = serializers.MultipleChoiceField(choices=choices.EXPERTISE_REGION_CHOICES, required=False)
    expertise_countries = serializers.MultipleChoiceField(choices=choices.COUNTRY_CHOICES, required=False)
    expertise_languages = serializers.MultipleChoiceField(choices=choices.EXPERTISE_LANGUAGES, required=False)
    expertise_products_services_labels = serializers.ListField(required=False)
    is_showcase_company = serializers.NullBooleanField(required=False)

    def validate(self, attrs):
        is_term_present = attrs.get('term') is not None
        is_optional_field_present = self.is_optional_field_present(attrs)
        if not (is_term_present or is_optional_field_present):
            raise serializers.ValidationError(self.MESSAGE_MISSING_QUERY)
        return {key: value for key, value in attrs.items() if value}

    def is_optional_field_present(self, attrs):
        for field in self.OPTIONAL_FILTERS:
            if attrs.get(field) is not None:
                return True
        return False


class VerifyCompanyWithCompaniesHouseSerializer(serializers.Serializer):
    MESSAGE_BAD_ACCESS_TOKEN = 'Bad access token'
    MESSAGE_SCOPE_ERROR = 'Access token not valid for company'
    MESSAGE_EXPIRED = 'Access token has expired'

    access_token = serializers.CharField()

    def validate_access_token(self, value):
        response = CompaniesHouseClient.verify_access_token(value)
        if not response.ok:
            raise serializers.ValidationError(self.MESSAGE_BAD_ACCESS_TOKEN)
        data = response.json()
        if not data['scope'].rsplit('/')[-1] == self.context['company_number']:
            raise serializers.ValidationError(self.MESSAGE_SCOPE_ERROR)
        if data['expires_in'] < 1:
            raise serializers.ValidationError(self.MESSAGE_EXPIRED)


class RemoveCollaboratorsSerializer(serializers.Serializer):
    sso_ids = serializers.ListField(child=serializers.IntegerField())


class CollaborationRequestSerializer(serializers.ModelSerializer):

    requestor_sso_id = serializers.IntegerField(
        source='requestor.sso_id', required=False, read_only=True
    )

    class Meta:

        model = models.CollaborationRequest
        fields = (
            'uuid',
            'requestor',
            'requestor_sso_id',
            'name',
            'role',
            'accepted',
            'accepted_date',
        )
        extra_kwargs = {
            'requestor': {'required': False},  # passed in .save by the view, not in the request
            'name': {'required': False},  # passed in .save by the view, not in the request
            'uuid': {'read_only': True},
            'accepted': {'required': False},
        }

    def update(self, instance, validated_data):
        if validated_data.get('accepted') is True:
            validated_data['accepted_date'] = now()
            instance.requestor.role = instance.role
        return super().update(instance, validated_data)


class CollaborationInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CollaborationInvite
        fields = (
            'uuid',
            'collaborator_email',
            'company',
            'company_user',
            'accepted',
            'accepted_date',
            'role',
        )
        extra_kwargs = {
            'company': {'required': False},  # passed in .save by the view, not in the request
            'company_user': {'required': False},  # passed in .save by the view, not in the request
            'uuid': {'read_only': True},
            'accepted': {'required': False},
        }

    def update(self, instance, validated_data):
        if validated_data.get('accepted') is True:
            validated_data['accepted_date'] = now()
            self.update_or_create_supplier(instance, self.context['request'].user.full_name)
        return super().update(instance, validated_data)

    def update_or_create_supplier(self, collaborator_invite, name):
        models.CompanyUser.objects.update_or_create(
            sso_id=self.context['request'].user.id,
            company_email=collaborator_invite.collaborator_email,
            name=name,
            defaults={
                'company': collaborator_invite.company,
                'role': collaborator_invite.role,
            }
        )


class AddCollaboratorSerializer(serializers.ModelSerializer):

    company = serializers.SlugRelatedField(slug_field='number', queryset=models.Company.objects.all())

    class Meta:
        model = models.CompanyUser
        fields = (
            'sso_id',
            'name',
            'company',
            'company_email',
            'mobile_number',
            'role'
        )

        extra_kwargs = {
            'role': {
                'default': user_roles.MEMBER
            }
        }


class ChangeCollaboratorRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CompanyUser
        fields = ('role',)


class ExternalCompanyUserSerializer(serializers.ModelSerializer):

    company_number = serializers.ReadOnlyField(source='company.number')
    company_name = serializers.ReadOnlyField(source='company.name')
    company_export_status = serializers.ReadOnlyField(source='company.export_status')
    company_has_exported_before = serializers.ReadOnlyField(source='company.has_exported_before')
    company_industries = serializers.ReadOnlyField(source='company.sectors')
    profile_url = serializers.SerializerMethodField()

    class Meta:
        model = models.CompanyUser
        fields = (
            'company_email',
            'company_export_status',
            'company_has_exported_before',
            'company_industries',
            'company_number',
            'company_name',
            'name',
            'profile_url',
            'sso_id',
            'is_company_owner',
            'role',
        )
        extra_kwargs = {
            'role': {'read_only': True},
        }

    def get_profile_url(self, obj):
        return obj.company.public_profile_url


class CompanyUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CompanyUser
        fields = (
            'company',
            'company_email',
            'date_joined',
            'sso_id',
            'is_company_owner',
            'role',
            'name',
        )
        extra_kwargs = {
            'sso_id': {'required': True},
            'company': {'required': False},
            'role': {'read_only': True},
        }
