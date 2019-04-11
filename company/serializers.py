from django.utils.timezone import now
from rest_framework import serializers

from directory_validators import company as shared_validators
from directory_constants.constants import choices

from django.conf import settings
from django.http import QueryDict

from company import helpers, models, validators
from supplier.models import Supplier


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

    def to_internal_value(self, data):
        if isinstance(data, QueryDict):
            data = data.dict()
        data['company'] = self.context['request'].user.supplier.company.pk
        return super().to_internal_value(data)


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
            'company_type',
            'country',
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
            'website',
            'verified_with_code',
            'verified_with_preverified_enrolment',
            'verified_with_companies_house_oauth2',
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


class SearchSerializer(serializers.Serializer):

    MESSAGE_MISSING_QUERY = 'Please specify a term, sector'

    term = serializers.CharField(required=False)
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    sectors = serializers.MultipleChoiceField(
        choices=choices.INDUSTRIES,
        required=False,
    )

    is_showcase_company = serializers.NullBooleanField(required=False)

    def validate(self, attrs):
        is_sector_present = attrs.get('sectors') is not None
        is_term_present = attrs.get('term') is not None
        if not (is_term_present or is_sector_present):
            raise serializers.ValidationError(self.MESSAGE_MISSING_QUERY)
        return attrs


class VerifyCompanyWithCompaniesHouseSerializer(serializers.Serializer):
    MESSAGE_BAD_ACCESS_TOKEN = 'Bad access token'
    MESSAGE_SCOPE_ERROR = 'Access token not valid for company'
    MESSAGE_EXPIRED = 'Access token has expired'

    access_token = serializers.CharField()

    def validate_access_token(self, value):
        response = helpers.CompaniesHouseClient.verify_access_token(value)
        if not response.ok:
            raise serializers.ValidationError(self.MESSAGE_BAD_ACCESS_TOKEN)
        data = response.json()
        if not data['scope'].rsplit('/')[-1] == self.context['company_number']:
            raise serializers.ValidationError(self.MESSAGE_SCOPE_ERROR)
        if data['expires_in'] < 1:
            raise serializers.ValidationError(self.MESSAGE_EXPIRED)


class InviteSerializerMixin:

    MESSAGE_ALREADY_HAS_COMPANY = 'User already has a company'
    MESSAGE_WRONG_INVITE = 'User accepting an incorrect invite'
    MESSAGE_INVALID_REQUESTOR = 'Requestor is not legit'

    def to_internal_value(self, data):
        if isinstance(data, QueryDict):
            data = data.dict()
        if not self.partial:
            data['requestor'] = self.context['request'].user.supplier.pk
            data['company'] = self.context['request'].user.supplier.company.pk
        return super().to_internal_value(data)

    def validate(self, data):
        if data.get('accepted', False):
            self.check_different_company_connection()
            self.check_email()
            self.check_requestor()
        return super().validate(data)

    def update(self, instance, validated_data):
        if validated_data.get('accepted') is True:
            validated_data['accepted_date'] = now()
        instance = super().update(instance, validated_data)
        self.update_or_create_supplier(instance)
        return instance

    def check_different_company_connection(self):
        user = self.context['request'].user
        if (
            user.supplier and
            user.supplier.company and
            user.supplier.company != self.instance.company
        ):
            raise serializers.ValidationError({
                self.email_field_name: self.MESSAGE_ALREADY_HAS_COMPANY
            })

    def check_email(self):
        user = self.context['request'].user
        email_value = getattr(self.instance, self.email_field_name)
        if email_value.lower() != user.email.lower():
            raise serializers.ValidationError({
                self.email_field_name: self.MESSAGE_WRONG_INVITE
            })

    def check_requestor(self):
        queryset = self.instance.company.suppliers.all()
        if self.instance.requestor not in queryset:
            raise serializers.ValidationError({
                'requestor': self.MESSAGE_INVALID_REQUESTOR
            })


class OwnershipInviteSerializer(
    InviteSerializerMixin, serializers.ModelSerializer
):
    email_field_name = 'new_owner_email'

    company_name = serializers.CharField(read_only=True, source='company.name')

    class Meta:
        model = models.OwnershipInvite
        fields = (
            'accepted',
            'company',
            'company_name',
            'new_owner_email',
            'requestor',
            'uuid',
        )

        extra_kwargs = {
            'accepted': {'write_only': True},
            'company': {'required': False},
            'requestor': {'required': False},
            'uuid': {'read_only': True},
        }

    def update_or_create_supplier(self, instance):
        Supplier.objects.update_or_create(
            sso_id=self.context['request'].user.id,
            company_email=instance.new_owner_email,
            defaults={
                'company': instance.company,
                'is_company_owner': True,
            }
        )


class CollaboratorInviteSerializer(
    InviteSerializerMixin, serializers.ModelSerializer
):
    email_field_name = 'collaborator_email'

    company_name = serializers.CharField(read_only=True, source='company.name')

    class Meta:
        model = models.CollaboratorInvite
        fields = (
            'accepted',
            'collaborator_email',
            'company',
            'company_name',
            'requestor',
            'uuid',
        )
        extra_kwargs = {
            'accepted': {'write_only': True},
            'company': {'read_only': False},
            'requestor': {'required': False},
            'uuid': {'read_only': True},
        }

    def update_or_create_supplier(self, instance):
        Supplier.objects.update_or_create(
            sso_id=self.context['request'].user.id,
            company_email=instance.collaborator_email,
            defaults={
                'company': instance.company,
                'is_company_owner': False,
            }
        )


class RemoveCollaboratorsSerializer(serializers.Serializer):
    sso_ids = serializers.ListField(
        child=serializers.IntegerField()
    )


class CollaboratorRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CollaboratorRequest
        fields = (
            'collaborator_email',
            'company',
        )

    def to_internal_value(self, data):
        if isinstance(data, QueryDict):
            data = data.dict()
        try:
            company = models.Company.objects.get(number=data['company_number'])
        except models.Company.DoesNotExist:
            raise serializers.ValidationError({
                '__all__': 'Company does not exist'
            })
        else:
            data['company'] = company.pk
        return super().to_internal_value(data)
