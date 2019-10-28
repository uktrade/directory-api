import random

from rest_framework.serializers import (
    Serializer,
    CharField,
    ListField,
    ModelSerializer,
)
from directory_constants import choices, sectors, expertise

from company.tests import factories
from company.models import Company


class CompanySerializer(ModelSerializer):

    class Meta:
        model = Company
        fields = (
            'number',
            'verification_code',
            'email_address',
            'is_verification_letter_sent',
            'is_identity_check_message_sent',
            'verified_with_identity_check',
            'verified_with_code',
        )
        extra_kwargs = {}


class ISDCompanySerializer(ModelSerializer):

    class Meta:
        model = Company
        fields = '__all__'
        extra_kwargs = {
            'slug': {
                'required': False
            },
            'name': {
                'required': False
            },
            'is_uk_isd_company': {
                'required': False,
                'default': True,
            },
        }

    @staticmethod
    def slice_choices(list_of_choice_tuples, max_items=None):
        return [
            choice[0]
            for choice in random.sample(
                list_of_choice_tuples,
                random.randint(
                    0, max_items if max_items else len(list_of_choice_tuples)
                )
            )
        ]

    @staticmethod
    def slice_list(list_of_strings, max_items=None):
        return random.sample(
            list_of_strings,
            random.randint(0, max_items if max_items else len(list_of_strings))
        )

    def create(self, validated_data):
        number = f'AT{random.randint(0, 999999):06}'
        countries = self.slice_choices(
            choices.COUNTRY_CHOICES, max_items=15)
        languages = self.slice_choices(
            choices.EXPERTISE_LANGUAGES, max_items=15)
        regions = self.slice_choices(
            choices.EXPERTISE_REGION_CHOICES, max_items=5)
        industries = random.sample(
            [
                item
                for item in dir(sectors)
                if not item.startswith('__') and item != sectors.CONFLATED
            ],
            random.randint(0, 10)
        )
        wolf_company = factories.CompanyFactory(
            number=number,
            name=f'Automated tests {number}',
            description='Delete at will',
            summary='Hunts in packs common',
            is_uk_isd_company=validated_data.get('is_uk_isd_company', True),
            is_published_investment_support_directory=False,
            is_published_find_a_supplier=False,
            keywords='Automated tests, Packs, Hunting, Stark, Teeth',
            expertise_industries=industries,
            expertise_regions=regions,
            expertise_languages=languages,
            expertise_countries=countries,
            expertise_products_services={
                'other': ['Regulatory', 'Finance', 'IT'],
                'Finance': self.slice_list(expertise.FINANCIAL),
                'Management Consulting':
                    self.slice_list(expertise.MANAGEMENT_CONSULTING),
                'Human Resources': self.slice_list(expertise.HUMAN_RESOURCES),
                'Legal': self.slice_list(expertise.LEGAL),
                'Publicity': self.slice_list(expertise.PUBLICITY),
                'Business Support':
                    self.slice_list(expertise.BUSINESS_SUPPORT),
            },
            website=f'https://automated.tests.{number}.com',
            email_address='',
            email_full_name='',
            slug=f'auto-tests-isd-company-{number}',
            twitter_url=f'http://twitter.com/automated-tests-{number}',
            facebook_url=f'http://facebook.com/automated-tests-{number}',
            linkedin_url=f'http://linkedin.com/automated-tests-{number}',
        )
        return wolf_company


class PublishedCompaniesSerializer(Serializer):

    name = CharField(read_only=True)
    number = CharField(read_only=True)
    sectors = ListField(read_only=True)
    employees = CharField(read_only=True)
    keywords = ListField(read_only=True)
    website = CharField(read_only=True)
    facebook_url = CharField(read_only=True)
    linkedin_url = CharField(read_only=True)
    twitter_url = CharField(read_only=True)
    company_email = CharField(read_only=True)
    summary = CharField(read_only=True)
    description = CharField(read_only=True)
