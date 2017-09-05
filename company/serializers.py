from django.utils.timezone import now
from rest_framework import serializers

from directory_validators import company as shared_validators
from directory_constants.constants import choices

from django.conf import settings

from company import helpers, models, validators


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
            'facebook_url',
            'has_exported_before',
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
            'website',
            'verified_with_code',
            'verified_with_preverified_enrolment',
            'verified_with_companies_house_oauth2',
            'is_verified',
            'export_destinations',
            'export_destinations_other',
        )
        extra_kwargs = {
            'export_status': {'required': False},
            'has_exported_before': {'required': False},
            'modified': {'read_only': True},
            'is_published': {'read_only': True},
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


class CompanySearchSerializer(serializers.Serializer):

    MESSAGE_MISSING_SECTOR_TERM = 'Please specify a search term or a sector.'

    term = serializers.CharField(required=False)
    page = serializers.IntegerField()
    size = serializers.IntegerField()
    sectors = serializers.MultipleChoiceField(
        choices=choices.INDUSTRIES,
        required=False,
    )

    def validate(self, attrs):
        is_sector_present = attrs.get('sectors') is not None
        is_term_present = attrs.get('term') is not None
        if not (is_term_present or is_sector_present):
            raise serializers.ValidationError(self.MESSAGE_MISSING_SECTOR_TERM)
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


class SetRequestorCompanyMixin:
    def to_internal_value(self, data):
        data['requestor'] = self.context['request'].user.supplier.pk
        data['company'] = self.context['request'].user.supplier.company.pk
        return super().to_internal_value(data)


class OwershipInviteSerializer(
    SetRequestorCompanyMixin, serializers.ModelSerializer
):
    company_name = serializers.CharField(read_only=True, source='company.name')

    def validate_new_owner_email(self, value):
        if not self.partial:
            return value
        user = self.context['request'].user
        if user.supplier is not None:
            serializers.ValidationError('User has already a company')
        if value != user.company_email:
            raise serializers.ValidationError(
                'User accepting an incorrect invite'
            )
        return value

    def validate_requestor(self, value):
        if not self.partial:
            return value
        if self.instance.company.suppliers != self.instance.requestor:
            raise serializers.ValidationError('Requestor is not legit')
        return value


class OwnershipInviteSerializer(
    SetRequestorCompanyMixin, serializers.ModelSerializer
):
    class Meta:
        model = OwnershipInvite
        fields = (
            'new_owner_email',
            'company_name',
            'company',
            'requestor',
            'uuid'
        )
        extra_kwargs = {
            'uuid': {'read_only': True}
        }


class CollaboratorInviteSerializer(
    SetRequestorCompanyMixin, serializers.ModelSerializer
):

    class Meta:
        model = models.CollaboratorInvite
        fields = (
            'collaborator_email',
            'company',
            'requestor',
        )


class RemoveCollaboratorsSerializer(serializers.Serializer):
    sso_ids = serializers.ListField(
        child=serializers.IntegerField()
    )


class OwershipInviteSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(read_only=True, source='company.name')

    def validate_new_owner_email(self, value):
        if not self.partial:
            return value
        user = self.context['request'].user
        if user.supplier is not None:
            serializers.ValidationError('User has already a company')
        if value != user.company_email:
            raise serializers.ValidationError(
                'User accepting an incorrect invite'
            )
        return value

    def validate_requestor(self, value):
        if not self.partial:
            return value
        if self.instance.requestor not in self.instance.company.suppliers:
            raise serializers.ValidationError('Requestor is not legit')
        return value

    def update(self, instance, validated_data):
        if validated_data['accepted'] == True:
            validated_data['accepted_date'] = now()
        instance = super().update(instance, validated_data)
        self.create_supplier(instance)
        return instance

    def create_supplier(self, instance):
        from user.models import User as Supplier
        supplier = Supplier(
            sso_id=self.context['request'].user.id,
            company=instance.company,
            company_email=instance.company.email_address,
            is_company_owner=True,
        )
        supplier.save()

    class Meta:
        model = OwnershipInvite
        fields = (
            'new_owner_email',
            'company_name',
            'company',
            'requestor',
            'uuid',
            'accepted',
        )

        extra_kwargs = {
            'uuid': {'read_only': True},
            'accepted': {'write_only': True},
        }


class CollaboratorInviteSerializer(
    SetRequestorCompanyMixin, serializers.ModelSerializer
):
    company_name = serializers.CharField(read_only=True, source='company.name')

    class Meta:
        model = models.CollaboratorInvite
        fields = (
            'collaborator_email',
            'company_name',
            'requestor',
            'uuid',
        )
        extra_kwargs = {
            'uuid': {'read_only': True},
            'accepted': {'write_only': True},
        }


class RemoveCollaboratorsSerializer(serializers.Serializer):
    sso_ids = serializers.ListField(
        child=serializers.IntegerField()
    )
