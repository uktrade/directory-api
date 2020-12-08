from rest_framework import serializers

from company.models import Company


class ActivityStreamCompanySerializer(serializers.ModelSerializer):
    """
    Company serializer for activity stream.

    - Adds extra response fields required by activity stream.
    - Adds the required prefix to field names
    """

    class Meta:
        model = Company
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
            'mobile_number',
            'modified',
            'name',
            'number',
            'po_box',
            'postal_code',
            'postal_full_name',
            'sectors',
            'hs_codes',
            'slug',
            'summary',
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

    def to_representation(self, instance):
        """
        Prefix field names to match activity stream format
        """
        prefix = 'dit:directory:Company'
        return {
            'id': f'{prefix}:{instance.id}:Update',
            'published': instance.date_published.isoformat(),
            'generator': {
                'type': 'Application',
                'name': 'dit:directory',
            },
            'object': {
                'id': f'{prefix}:{instance.id}',
                'type': 'dit:directory:Company',
                **{f'{prefix}:{k}': v for k, v in super().to_representation(instance).items()},
            },
        }
