import base64
import datetime
import http
from io import BytesIO
from unittest import mock

import pytest
from directory_constants import choices, company_types, sectors, user_roles
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse
from elasticsearch_dsl import Index
from elasticsearch_dsl.connections import connections
from freezegun import freeze_time
from PIL import Image
from rest_framework import status
from rest_framework.test import APIClient

from company import helpers, models, serializers
from company.tests import (
    VALID_REQUEST_DATA,
    VALID_SUPPLIER_REQUEST_DATA,
    MockInvalidSerializer,
    MockValidSerializer,
    factories,
)
from core.helpers import CompaniesHouseClient, SSOUser
from core.tests.test_views import reload_module, reload_urlconf

default_public_profile_data = {
    'name': 'private company',
    'website': 'http://example.com',
    'description': 'Company description',
    'has_exported_before': True,
    'date_of_creation': '2010-10-10',
    'email_address': 'thing@example.com',
    'verified_with_code': True,
}


default_ordering_values = {
    'keywords': '',
    'sectors': [],
    'hs_codes': [],
    'expertise_industries': [],
    'expertise_regions': [],
    'expertise_languages': [],
    'expertise_countries': [],
    'expertise_products_services': {},
    'is_published_investment_support_directory': True,
    'is_published_find_a_supplier': True,
}


@pytest.mark.django_db
def test_company_retrieve_no_company(authed_client, authed_supplier):
    authed_supplier.company = None
    authed_supplier.save()

    response = authed_client.get(reverse('company'))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@freeze_time('2016-11-23T11:21:10.977518Z')
@pytest.mark.django_db
def test_company_retrieve_view(authed_client, authed_supplier):
    company = factories.CompanyFactory(name='Test Company', date_of_creation=datetime.date(2000, 10, 10))
    authed_supplier.company = company
    authed_supplier.save()

    response = authed_client.get(reverse('company'))

    expected = {
        'address_line_1': company.address_line_1,
        'address_line_2': company.address_line_2,
        'company_type': company_types.COMPANIES_HOUSE,
        'country': company.country,
        'date_of_creation': '2000-10-10',
        'description': company.description,
        'email_address': company.email_address,
        'email_full_name': company.email_full_name,
        'employees': company.employees,
        'expertise_countries': company.expertise_countries,
        'expertise_industries': company.expertise_industries,
        'expertise_languages': company.expertise_languages,
        'expertise_products_services': company.expertise_products_services,
        'expertise_regions': company.expertise_regions,
        'export_destinations': [],
        'export_destinations_other': '',
        'facebook_url': company.facebook_url,
        'has_exported_before': company.has_exported_before,
        'has_valid_address': True,
        'hs_codes': company.hs_codes,
        'id': str(company.id),
        'is_exporting_goods': False,
        'is_exporting_services': False,
        'is_identity_check_message_sent': False,
        'is_publishable': company.is_publishable,
        'is_published': False,
        'is_published_find_a_supplier': False,
        'is_published_investment_support_directory': False,
        'is_registration_letter_sent': False,
        'is_uk_isd_company': False,
        'is_verification_letter_sent': False,
        'is_verified': False,
        'keywords': company.keywords,
        'linkedin_url': company.linkedin_url,
        'locality': company.locality,
        'logo': None,
        'mobile_number': company.mobile_number,
        'created': '2016-11-23T11:21:10.977518Z',
        'modified': '2016-11-23T11:21:10.977518Z',
        'name': 'Test Company',
        'number': company.number,
        'po_box': company.po_box,
        'postal_code': company.postal_code,
        'postal_full_name': company.postal_full_name,
        'sectors': company.sectors,
        'slug': 'test-company',
        'summary': company.summary,
        'supplier_case_studies': [],
        'twitter_url': company.twitter_url,
        'verified_with_code': False,
        'verified_with_companies_house_oauth2': False,
        'verified_with_identity_check': False,
        'verified_with_preverified_enrolment': False,
        'website': company.website,
    }

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@freeze_time('2016-11-23T11:21:10.977518Z')
@pytest.mark.django_db
def test_company_update_with_put(authed_client, authed_supplier):
    company = factories.CompanyFactory(
        number='01234567',
        has_exported_before=True,
    )
    authed_supplier.company = company
    authed_supplier.save()

    response = authed_client.put(reverse('company'), VALID_REQUEST_DATA, format='json')

    expected = {
        'company_type': company_types.COMPANIES_HOUSE,
        'email_address': company.email_address,
        'email_full_name': company.email_full_name,
        'employees': company.employees,
        'expertise_countries': company.expertise_countries,
        'expertise_industries': company.expertise_industries,
        'expertise_languages': company.expertise_languages,
        'expertise_products_services': company.expertise_products_services,
        'expertise_regions': company.expertise_regions,
        'export_destinations': ['DE'],
        'export_destinations_other': 'LY',
        'facebook_url': company.facebook_url,
        'has_valid_address': True,
        'hs_codes': company.hs_codes,
        'id': str(company.id),
        'is_exporting_goods': False,
        'is_exporting_services': False,
        'is_identity_check_message_sent': False,
        'is_publishable': company.is_publishable,
        'is_published': False,
        'is_published_find_a_supplier': False,
        'is_published_investment_support_directory': False,
        'is_registration_letter_sent': False,
        'is_uk_isd_company': False,
        'is_verification_letter_sent': False,
        'is_verified': False,
        'keywords': company.keywords,
        'linkedin_url': company.linkedin_url,
        'logo': None,
        'created': '2016-11-23T11:21:10.977518Z',
        'modified': '2016-11-23T11:21:10.977518Z',
        'po_box': company.po_box,
        'sectors': company.sectors,
        'slug': 'test-company',
        'summary': company.summary,
        'supplier_case_studies': [],
        'twitter_url': company.twitter_url,
        'verified_with_code': False,
        'verified_with_companies_house_oauth2': False,
        'verified_with_identity_check': False,
        'verified_with_preverified_enrolment': False,
    }
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@freeze_time('2016-11-23T11:21:10.977518Z')
@pytest.mark.django_db
def test_company_partial_update(authed_client, authed_supplier):
    company = factories.CompanyFactory(
        number='01234567',
    )
    authed_supplier.company = company
    authed_supplier.save()

    response = authed_client.patch(reverse('company'), VALID_REQUEST_DATA, format='json')

    expected = {
        'company_type': company_types.COMPANIES_HOUSE,
        'email_address': company.email_address,
        'email_full_name': company.email_full_name,
        'employees': company.employees,
        'expertise_countries': company.expertise_countries,
        'expertise_industries': company.expertise_industries,
        'expertise_languages': company.expertise_languages,
        'expertise_products_services': company.expertise_products_services,
        'expertise_regions': company.expertise_regions,
        'export_destinations': ['DE'],
        'export_destinations_other': 'LY',
        'facebook_url': company.facebook_url,
        'has_valid_address': True,
        'hs_codes': company.hs_codes,
        'id': str(company.id),
        'is_exporting_goods': False,
        'is_exporting_services': False,
        'is_identity_check_message_sent': False,
        'is_publishable': company.is_publishable,
        'is_published': False,
        'is_published_find_a_supplier': False,
        'is_published_investment_support_directory': False,
        'is_registration_letter_sent': False,
        'is_uk_isd_company': False,
        'is_verification_letter_sent': False,
        'is_verified': False,
        'keywords': company.keywords,
        'linkedin_url': company.linkedin_url,
        'logo': None,
        'created': '2016-11-23T11:21:10.977518Z',
        'modified': '2016-11-23T11:21:10.977518Z',
        'po_box': company.po_box,
        'sectors': company.sectors,
        'slug': 'test-company',
        'summary': company.summary,
        'supplier_case_studies': [],
        'twitter_url': company.twitter_url,
        'verified_with_code': False,
        'verified_with_companies_house_oauth2': False,
        'verified_with_identity_check': False,
        'verified_with_preverified_enrolment': False,
    }
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@freeze_time('2016-11-23T11:21:10.977518Z')
@pytest.mark.django_db
def test_company_partial_update_no_company(authed_client, authed_supplier):
    # make the user logged in but no supplier attached to them
    authed_supplier.delete()

    data = {
        'name': 'Example company',
        'sectors': ['SOFTWARE_AND_COMPUTER_SERVICES'],
        'hs_codes': ['3'],
        'expertise_industries': [sectors.AEROSPACE, sectors.AIRPORTS],
        'expertise_countries': [choices.COUNTRY_CHOICES[23][0], choices.COUNTRY_CHOICES[24][0]],
    }

    response = authed_client.patch(reverse('company'), data, format='json')

    assert response.status_code == status.HTTP_200_OK

    company = models.Company.objects.get(company_users__sso_id=authed_supplier.sso_id)
    assert company.name == data['name']
    assert company.sectors == data['sectors']
    assert company.hs_codes == data['hs_codes']
    assert company.expertise_industries == data['expertise_industries']
    assert company.expertise_countries == data['expertise_countries']
    assert models.CompanyUser.objects.get(sso_id=authed_supplier.sso_id, company=company)


@freeze_time('2016-11-23T11:21:10.977518Z')
@pytest.mark.django_db
def test_company_not_update_modified(authed_client, authed_supplier):
    company = factories.CompanyFactory(
        number='01234567',
        has_exported_before=True,
    )
    authed_supplier.company = company
    authed_supplier.save()

    data = {**VALID_REQUEST_DATA, 'modified': '2013-03-09T23:28:53.977518Z'}
    for method in [authed_client.put, authed_client.patch]:
        response = method(reverse('company'), data, format='json')
        assert response.status_code == status.HTTP_200_OK
        # modified was not effected by the data we tried to pass
        assert response.json()['modified'] == '2016-11-23T11:21:10.977518Z'


@pytest.mark.django_db
@mock.patch('company.views.CompanyNumberValidatorAPIView.get_serializer')
def test_company_number_validator_rejects_invalid_data(mock_get_serializer, client):
    serializer = MockInvalidSerializer(data={})
    mock_get_serializer.return_value = serializer
    response = client.get(reverse('validate-company-number'), {})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == serializer.errors


@pytest.mark.django_db
@mock.patch('company.views.CompanyNumberValidatorAPIView.get_serializer')
def test_company_number_validator_accepts_valid_data(mock_get_serializer, client):
    mock_get_serializer.return_value = MockValidSerializer(data={})
    response = client.get(reverse('validate-company-number'), {})
    assert response.status_code == status.HTTP_200_OK


def get_test_image(extension='png'):
    bytes_io = BytesIO()
    Image.new('RGB', (300, 50)).save(bytes_io, extension)
    bytes_io.seek(0)
    return SimpleUploadedFile(f'test.{extension}', bytes_io.read())


@pytest.fixture(scope='session')
def image_one(tmpdir_factory):
    return get_test_image()


@pytest.fixture(scope='session')
def image_two(tmpdir_factory):
    return get_test_image()


@pytest.fixture(scope='session')
def image_three(tmpdir_factory):
    return get_test_image()


@pytest.fixture(scope='session')
def video(tmpdir_factory):
    return BytesIO(b'some text')


@pytest.fixture
def case_study_data(image_one, image_two, image_three, video, company):
    return {
        'company': company.pk,
        'title': 'a title',
        'description': 'a description',
        'sector': choices.INDUSTRIES[1][0],
        'website': 'http://www.example.com',
        'keywords': 'good, great',
        'image_one': image_one,
        'image_two': image_two,
        'image_three': image_three,
        'video_one': video,
        'testimonial': 'very nice',
        'testimonial_name': 'Lord Voldemort',
        'testimonial_job_title': 'Evil overlord',
        'testimonial_company': 'Death Eaters',
    }


@pytest.fixture
def company_data():
    return {
        'number': '01234567',
        'name': 'Test Company',
        'website': 'http://example.com',
        'description': 'Company description',
        'has_exported_before': True,
        'date_of_creation': '2010-10-10',
    }


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def company():
    return models.Company.objects.create(
        verified_with_code=True, email_address='test@example.com', **VALID_REQUEST_DATA
    )


@pytest.fixture
def private_profile():
    company = models.Company(**default_public_profile_data)
    company.number = '0123456A'
    company.verified_with_code = False
    company.save()
    return company


@pytest.fixture
def public_profile():
    company = models.Company(**default_public_profile_data)
    company.number = '0123456B'
    company.is_published_find_a_supplier = True
    company.save()
    return company


@pytest.fixture
def public_profile_with_case_study():
    company = factories.CompanyFactory(is_published_find_a_supplier=True)
    factories.CompanyCaseStudyFactory(company=company)
    return company


@pytest.fixture
def public_profile_with_case_studies():
    company = factories.CompanyFactory(is_published_find_a_supplier=True)
    factories.CompanyCaseStudyFactory(company=company)
    factories.CompanyCaseStudyFactory(company=company)
    return company


@pytest.fixture
def public_profile_software():
    company = models.Company(**default_public_profile_data)
    company.number = '0123456C'
    company.is_published_find_a_supplier = True
    company.sectors = ['SOFTWARE_AND_COMPUTER_SERVICES']
    company.save()
    return company


@pytest.fixture
def public_profile_cars():
    company = models.Company(**default_public_profile_data)
    company.number = '0123456D'
    company.is_published_find_a_supplier = True
    company.sectors = ['AUTOMOTIVE']
    company.save()
    return company


@pytest.fixture
def public_profile_smart_cars():
    company = models.Company(**default_public_profile_data)
    company.number = '0123456E'
    company.is_published_find_a_supplier = True
    company.sectors = ['SOFTWARE_AND_COMPUTER_SERVICES', 'AUTOMOTIVE']
    company.save()
    return company


@pytest.fixture
def company_user_case_study(case_study_data, company):
    return models.CompanyCaseStudy.objects.create(
        title=case_study_data['title'],
        description=case_study_data['description'],
        sector=case_study_data['sector'],
        website=case_study_data['website'],
        keywords=case_study_data['keywords'],
        testimonial=case_study_data['testimonial'],
        testimonial_name=case_study_data['testimonial_name'],
        testimonial_job_title=case_study_data['testimonial_job_title'],
        testimonial_company=case_study_data['testimonial_company'],
        company=company,
    )


@pytest.fixture
def supplier(company):
    return models.CompanyUser.objects.create(
        sso_id=2,
        company_email='someone@example.com',
        company=company,
    )


@pytest.fixture
def search_data(settings):
    wolf_company = factories.CompanyFactory(
        name='Wolf limited',
        description='Providing the stealth and prowess of wolves.',
        summary='Hunts in packs common',
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        keywords='Packs, Hunting, Stark, Teeth',
        expertise_industries=[sectors.AEROSPACE, sectors.AIRPORTS],
        expertise_regions=[choices.EXPERTISE_REGION_CHOICES[4][0], choices.EXPERTISE_REGION_CHOICES[5][0]],
        expertise_languages=[choices.EXPERTISE_LANGUAGES[0][0], choices.EXPERTISE_LANGUAGES[2][0]],
        expertise_countries=[choices.COUNTRY_CHOICES[23][0], choices.COUNTRY_CHOICES[24][0]],
        expertise_products_services={'other': ['Regulatory', 'Finance', 'IT']},
        id=1,
    )
    aardvark_company = factories.CompanyFactory(
        name='Aardvark limited',
        description='Providing the power and beauty of Aardvarks.',
        summary='Like an Aardvark common',
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        keywords='Ants, Tongue, Anteater',
        expertise_industries=[sectors.AEROSPACE],
        expertise_regions=[choices.EXPERTISE_REGION_CHOICES[4][0]],
        expertise_languages=[choices.EXPERTISE_LANGUAGES[0][0]],
        expertise_countries=[choices.COUNTRY_CHOICES[23][0]],
        expertise_products_services={'other': ['Regulatory', 'Finance', 'IT']},
        id=2,
    )
    factories.CompanyFactory(
        name='Grapeshot limited',
        description='Providing the destructiveness of grapeshot.',
        summary='Like naval warfare common',
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        keywords='Pirates, Ocean, Ship',
        expertise_industries=[sectors.AIRPORTS, sectors.FOOD_AND_DRINK],
        expertise_regions=[choices.EXPERTISE_REGION_CHOICES[5][0], choices.EXPERTISE_REGION_CHOICES[8][0]],
        expertise_languages=[choices.EXPERTISE_LANGUAGES[2][0], choices.EXPERTISE_LANGUAGES[6][0]],
        expertise_countries=[choices.COUNTRY_CHOICES[24][0], choices.COUNTRY_CHOICES[27][0]],
        expertise_products_services={'other': ['Regulatory', 'IT']},
        id=3,
    )
    factories.CompanyCaseStudyFactory(
        id=1,
        company=wolf_company,
        title='Thick case study',
        description='Gold is delicious.',
    )
    factories.CompanyCaseStudyFactory(
        id=2,
        company=aardvark_company,
        title='Thick case study',
        description='We determined lead sinks in water.',
    )
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()


@pytest.fixture
def search_companies_highlighting_data(settings):
    factories.CompanyFactory(
        name='Wolf limited',
        description=(
            'Providing the stealth and prowess of wolves. This is a very long '
            'thing about wolf stuff. Lets see what happens in the test when '
            'ES encounters a long  description. Perhaps it will concatenate. '
        )
        + ('It is known. ' * 30)
        + ('The wolf cries at night.'),
        summary='Hunts in packs',
        is_published_find_a_supplier=True,
        keywords='Packs, Hunting, Stark, Teeth',
        sectors=[sectors.AEROSPACE, sectors.AIRPORTS],
        id=1,
    )
    factories.CompanyFactory(
        name='Aardvark limited',
        description='Providing the power and beauty of Aardvarks.',
        summary='Like an Aardvark',
        is_published_find_a_supplier=True,
        keywords='Ants, Tongue, Anteater',
        sectors=[sectors.AEROSPACE],
        id=2,
    )
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()


@pytest.fixture
def search_highlighting_data(settings):
    factories.CompanyFactory(
        name='Wolf limited',
        description=(
            'Providing the stealth and prowess of wolves. This is a very long '
            'thing about wolf stuff. Lets see what happens in the test when '
            'ES encounters a long  description. Perhaps it will concatenate. '
        )
        + ('It is known. ' * 30)
        + ('The wolf cries at night.'),
        summary='Hunts in packs',
        is_published_find_a_supplier=True,
        is_published_investment_support_directory=True,
        keywords='Packs, Hunting, Stark, Teeth',
        id=1,
    )
    factories.CompanyFactory(
        name='Aardvark limited',
        description='Providing the power and beauty of Aardvarks.',
        summary='Like an Aardvark',
        is_published_find_a_supplier=True,
        is_published_investment_support_directory=True,
        keywords='Ants, Tongue, Anteater',
        id=2,
    )
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()


@pytest.fixture
def search_data_and_or(settings):
    factories.CompanyFactory(
        name='Wolf limited',
        expertise_industries=[sectors.AEROSPACE],
        expertise_regions=['NORTH_EAST'],
        expertise_countries=['AF'],
        expertise_languages=['ab'],
        expertise_products_services={'financial': ['Accounting and tax']},
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        id=1,
    )
    factories.CompanyFactory(
        name='Wolf corp',
        expertise_industries=[sectors.AIRPORTS],
        expertise_regions=['NORTH_WEST'],
        expertise_languages=['aa'],
        expertise_countries=['AL'],
        expertise_products_services={'management-consulting': ['Business development']},
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        id=2,
    )
    factories.CompanyFactory(
        name='Wolf are us',
        expertise_industries=[sectors.AEROSPACE],
        expertise_regions=['NORTH_WEST'],
        expertise_languages=['aa'],
        expertise_countries=['AL'],
        expertise_products_services={},
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        id=3,
    )
    factories.CompanyFactory(
        name='Ultra Wolf',
        expertise_industries=[sectors.AEROSPACE],
        expertise_regions=['NORTH_WEST'],
        expertise_languages=['aa'],
        expertise_countries=[],
        expertise_products_services={'management-consulting': ['Business development']},
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        id=4,
    )
    factories.CompanyFactory(
        name='Wolf nation',
        expertise_industries=[sectors.AEROSPACE],
        expertise_regions=['NORTH_WEST'],
        expertise_languages=[],
        expertise_countries=['AL'],
        expertise_products_services={'management-consulting': ['Business development']},
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        id=5,
    )
    factories.CompanyFactory(
        name='company of the Wolf',
        expertise_industries=[sectors.AEROSPACE],
        expertise_regions=[],
        expertise_languages=['aa'],
        expertise_countries=['AL'],
        expertise_products_services={'management-consulting': ['Business development']},
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        id=6,
    )
    factories.CompanyFactory(
        name='year of the wolf',
        expertise_industries=[],
        expertise_regions=['NORTH_WEST'],
        expertise_languages=['aa'],
        expertise_countries=['AL'],
        expertise_products_services={'management-consulting': ['Business development']},
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        id=7,
    )
    factories.CompanyFactory(
        name='Fish corp',  # missing 'wolf match'
        expertise_industries=[sectors.AEROSPACE],
        expertise_regions=['NORTH_WEST'],
        expertise_languages=['aa'],
        expertise_countries=['AL'],
        expertise_products_services={'management-consulting': ['Business development']},
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        id=8,
    )
    factories.CompanyFactory(
        name='Wolf wild corp',
        expertise_industries=[sectors.AEROSPACE],
        expertise_regions=['NORTH_WEST'],
        expertise_languages=['aa'],
        expertise_countries=['AL'],
        expertise_products_services={'management-consulting': ['Business development']},
        is_published_investment_support_directory=False,  # not published
        is_published_find_a_supplier=False,  # not published
        id=9,
    )
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()


@pytest.fixture
def search_companies_ordering_data(settings):
    factories.CompanyFactory(
        name='Wolf limited',
        description='',
        summary='Hunts in packs',
        is_published_find_a_supplier=True,
        keywords='Packs, Hunting, Stark, Wolf',
        sectors=[sectors.AEROSPACE, sectors.AIRPORTS],
        id=1,
    )
    wolf_three = factories.CompanyFactory(
        name='Wolf from Gladiators limited',
        description='',
        summary='Hunters',
        is_published_find_a_supplier=True,
        keywords='Packs, Hunting, Stark, Teeth',
        sectors=[sectors.FOOD_AND_DRINK, sectors.AIRPORTS],
        id=2,
    )
    wolf_one_company = factories.CompanyFactory(
        name='Wolf a kimbo Limited',
        description='pack hunters',
        summary='Hunts in packs',
        is_published_find_a_supplier=True,
        keywords='Packs, Hunting, Stark, Teeth',
        sectors=[sectors.AEROSPACE, sectors.AIRPORTS],
        id=3,
    )
    wolf_two_company = factories.CompanyFactory(
        name='Wolf among us Limited',
        description='wolf among sheep',
        summary='wooly',
        is_published_find_a_supplier=True,
        keywords='Sheep, big bad, wolf',
        sectors=[sectors.AEROSPACE, sectors.AIRPORTS],
        id=4,
    )
    grapeshot_company = factories.CompanyFactory(
        name='Grapeshot limited',
        description='Providing the destructiveness of grapeshot.',
        summary='Like naval warfare',
        is_published_find_a_supplier=True,
        keywords='Pirates, Ocean, Ship',
        sectors=[sectors.AIRPORTS, sectors.FOOD_AND_DRINK],
        id=5,
    )

    factories.CompanyCaseStudyFactory(company=wolf_one_company)
    factories.CompanyCaseStudyFactory(company=wolf_one_company)
    factories.CompanyCaseStudyFactory(company=wolf_two_company)
    factories.CompanyCaseStudyFactory(company=wolf_two_company)
    factories.CompanyCaseStudyFactory(company=wolf_two_company)
    factories.CompanyCaseStudyFactory(company=wolf_three, title='cannons better than grapeshot', description='guns')
    factories.CompanyCaseStudyFactory(company=wolf_three)
    factories.CompanyCaseStudyFactory(company=grapeshot_company, title='cannons', description='guns')
    factories.CompanyCaseStudyFactory(company=grapeshot_company, title='cannons', description='naval guns')
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()


@pytest.fixture
def search_companies_stopwords(settings):

    factories.CompanyFactory(
        name='mycompany ltd',
        description='',
        summary='Hunts in packs',
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        website='https://dontgothere.com',
        linkedin_url='linkedin_url',
        twitter_url='test_url',
        facebook_url='facebook_url',
        keywords='Packs, Hunting, Stark, Wolf',
        sectors=[sectors.AEROSPACE, sectors.AIRPORTS],
        id=1,
    )

    factories.CompanyFactory(
        name='Wolf ltd',
        description='',
        summary='Hunts in packs',
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        website='https://dontgothere.com',
        linkedin_url='linkedin_url',
        twitter_url='test_url',
        facebook_url='facebook_url',
        keywords='Packs, Hunting, Stark, Wolf',
        sectors=[sectors.AEROSPACE, sectors.AIRPORTS],
        id=2,
    )

    factories.CompanyFactory(
        name='Wolf limited',
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        website='https://dontgothere.com',
        linkedin_url='linkedin_url',
        twitter_url='test_url',
        facebook_url='facebook_url',
        id=3,
    )

    factories.CompanyFactory(
        name='Wolf plc',
        is_published_investment_support_directory=True,
        is_published_find_a_supplier=True,
        website='https://dontgothere.com',
        linkedin_url='linkedin_url',
        twitter_url='test_url',
        facebook_url='facebook_url',
        id=4,
    )

    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()


@pytest.fixture
def companies_house_oauth_invalid_access_token(requests_mocker):
    return requests_mocker.get('https://account.companieshouse.gov.uk/oauth2/verify', status_code=400)


@pytest.fixture
def companies_house_oauth_wrong_company(requests_mocker, authed_supplier):
    scope = CompaniesHouseClient.endpoints['profile'].format(
        number='{number}rad'.format(number=authed_supplier.company.number)
    )
    return requests_mocker.get(
        'https://account.companieshouse.gov.uk/oauth2/verify',
        status_code=200,
        json={
            'scope': scope,
            'expires_in': 6000,
        },
    )


@pytest.fixture
def companies_house_oauth_expired_token(requests_mocker, authed_supplier):
    scope = CompaniesHouseClient.endpoints['profile'].format(number=authed_supplier.company.number)
    return requests_mocker.get(
        'https://account.companieshouse.gov.uk/oauth2/verify',
        status_code=200,
        json={
            'scope': scope,
            'expires_in': -1,
        },
    )


@pytest.fixture
def companies_house_oauth_valid_token(requests_mocker, authed_supplier):
    scope = CompaniesHouseClient.endpoints['profile'].format(number=authed_supplier.company.number)
    return requests_mocker.get(
        'https://account.companieshouse.gov.uk/oauth2/verify',
        status_code=200,
        json={
            'scope': scope,
            'expires_in': 6000,
        },
    )


@pytest.mark.django_db
def test_company_update(company_data, authed_client, authed_supplier, company):
    authed_supplier.company = company
    authed_supplier.save()

    response = authed_client.patch(reverse('company'), company_data)
    instance = models.Company.objects.get(number=response.data['number'])

    assert response.status_code == http.client.OK
    assert instance.number == '01234567'
    assert instance.name == 'Test Company'
    assert instance.website == 'http://example.com'
    assert instance.description == 'Company description'
    assert instance.has_exported_before is True
    assert instance.date_of_creation == datetime.date(2010, 10, 10)


@pytest.mark.django_db
def test_company_case_study_create(
    case_study_data, authed_client, authed_supplier, company, mock_elasticsearch_company_save
):
    authed_supplier.company = company
    authed_supplier.save()

    response = authed_client.post(reverse('company-case-study'), case_study_data, format='multipart')
    assert response.status_code == http.client.CREATED

    instance = models.CompanyCaseStudy.objects.get(pk=response.data['pk'])
    assert instance.testimonial == case_study_data['testimonial']
    assert instance.testimonial_name == case_study_data['testimonial_name']
    assert instance.testimonial_job_title == (case_study_data['testimonial_job_title'])
    assert instance.testimonial_company == (case_study_data['testimonial_company'])
    assert instance.website == case_study_data['website']
    assert instance.company == company
    assert instance.description == case_study_data['description']
    assert instance.title == case_study_data['title']
    assert instance.sector == case_study_data['sector']
    assert instance.keywords == case_study_data['keywords']


@pytest.mark.django_db
def test_company_case_study_create_invalid_image(authed_client, authed_supplier, company):
    authed_supplier.company = company
    authed_supplier.save()

    case_study_data = {
        'company': company.pk,
        'title': 'a title',
        'description': 'a description',
        'sector': choices.INDUSTRIES[1][0],
        'website': 'http://www.example.com',
        'keywords': 'good, great',
        'image_one': get_test_image(extension='BMP'),
        'image_two': get_test_image(extension='TIFF'),
        'image_three': get_test_image(extension='GIF'),
        'testimonial': 'very nice',
        'testimonial_name': 'Lord Voldemort',
        'testimonial_job_title': 'Evil overlord',
        'testimonial_company': 'Death Eaters',
    }
    response = authed_client.post(reverse('company-case-study'), case_study_data, format='multipart')

    assert response.status_code == http.client.BAD_REQUEST


@pytest.mark.django_db
def test_company_case_study_create_not_an_image(video, authed_client, authed_supplier, company):
    authed_supplier.company = company
    authed_supplier.save()

    case_study_data = {
        'company': company.pk,
        'title': 'a title',
        'description': 'a description',
        'sector': choices.INDUSTRIES[1][0],
        'website': 'http://www.example.com',
        'keywords': 'good, great',
        'image_one': video,
        'image_two': video,
        'image_three': video,
        'testimonial': 'very nice',
        'testimonial_name': 'Lord Voldemort',
        'testimonial_job_title': 'Evil overlord',
        'testimonial_company': 'Death Eaters',
    }
    response = authed_client.post(reverse('company-case-study'), case_study_data, format='multipart')

    assert response.status_code == http.client.BAD_REQUEST


@pytest.mark.django_db
def test_company_case_study_create_company_not_published(video, authed_client, authed_supplier):
    company = factories.CompanyFactory.create(
        number='01234567',
        has_exported_before=True,
        is_published_find_a_supplier=False,
        is_published_investment_support_directory=False,
    )
    authed_supplier.company = company
    authed_supplier.save()

    case_study_data = {
        'company': company.pk,
        'title': 'a title',
        'description': 'a description',
        'sector': choices.INDUSTRIES[1][0],
        'website': 'http://www.example.com',
        'keywords': 'good, great',
        'image_one': get_test_image(extension='png'),
        'testimonial': 'very nice',
        'testimonial_name': 'Lord Voldemort',
        'testimonial_job_title': 'Evil overlord',
        'testimonial_company': 'Death Eaters',
    }
    response = authed_client.post(reverse('company-case-study'), case_study_data, format='multipart')
    assert response.status_code == http.client.CREATED

    url = reverse('public-case-study-detail', kwargs={'pk': response.data['pk']})
    response = authed_client.get(url)

    assert response.status_code == http.client.NOT_FOUND


@pytest.mark.django_db
def test_company_case_study_update(
    company_user_case_study, authed_supplier, authed_client, mock_elasticsearch_company_save
):
    authed_supplier.company = company_user_case_study.company
    authed_supplier.save()

    url = reverse('company-case-study-detail', kwargs={'pk': company_user_case_study.pk})
    data = {'title': '2015'}

    assert company_user_case_study.title != data['title']

    response = authed_client.patch(url, data, format='multipart')
    company_user_case_study.refresh_from_db()

    assert response.status_code == http.client.OK
    assert company_user_case_study.title == data['title']


@pytest.mark.django_db
def test_company_case_study_delete(company_user_case_study, authed_supplier, authed_client):
    authed_supplier.company = company_user_case_study.company
    authed_supplier.save()

    pk = company_user_case_study.pk
    url = reverse('company-case-study-detail', kwargs={'pk': pk})

    response = authed_client.delete(url)

    assert response.status_code == http.client.NO_CONTENT
    assert models.CompanyCaseStudy.objects.filter(pk=pk).exists() is False


@pytest.mark.django_db
def test_company_case_study_get(company_user_case_study, authed_supplier, authed_client):
    authed_supplier.company = company_user_case_study.company
    authed_supplier.save()

    url = reverse('company-case-study-detail', kwargs={'pk': company_user_case_study.pk})

    response = authed_client.get(url)
    data = response.json()

    assert response.status_code == http.client.OK
    assert data['testimonial'] == company_user_case_study.testimonial
    assert data['testimonial_name'] == company_user_case_study.testimonial_name
    assert data['testimonial_job_title'] == company_user_case_study.testimonial_job_title
    assert data['testimonial_company'] == company_user_case_study.testimonial_company
    assert data['website'] == company_user_case_study.website
    assert data['description'] == company_user_case_study.description
    assert data['title'] == company_user_case_study.title
    assert data['sector'] == company_user_case_study.sector
    assert data['keywords'] == company_user_case_study.keywords
    assert isinstance(data['company'], dict)
    assert data['company']['id'] == company_user_case_study.company.pk


@pytest.mark.django_db
def test_public_company_case_study_get(company_user_case_study, supplier, api_client, company):
    company.is_published_find_a_supplier = True
    company.is_published_investment_support_directory = True
    company.save()

    url = reverse('public-case-study-detail', kwargs={'pk': company_user_case_study.pk})

    response = api_client.get(url)
    data = response.json()

    assert response.status_code == http.client.OK
    assert data['testimonial'] == company_user_case_study.testimonial
    assert data['testimonial_name'] == company_user_case_study.testimonial_name
    assert data['testimonial_job_title'] == (company_user_case_study.testimonial_job_title)
    assert data['testimonial_company'] == (company_user_case_study.testimonial_company)
    assert data['website'] == company_user_case_study.website
    assert data['description'] == company_user_case_study.description
    assert data['title'] == company_user_case_study.title
    assert data['sector'] == company_user_case_study.sector
    assert data['keywords'] == company_user_case_study.keywords
    assert isinstance(data['company'], dict)
    assert data['company']['id'] == company_user_case_study.company.pk


@pytest.mark.parametrize(
    'is_investment_support_directory, is_find_a_supplier',
    [
        [True, False],
        [False, True],
        [True, True],
    ],
)
@pytest.mark.django_db
def test_company_profile_public_retrieve_public_profile(
    is_investment_support_directory,
    is_find_a_supplier,
    public_profile,
    api_client,
):
    public_profile.is_published_investment_support_directory = is_investment_support_directory
    public_profile.is_published_find_a_supplier = is_find_a_supplier

    public_profile.save()
    url = reverse('company-public-profile-detail', kwargs={'companies_house_number': public_profile.number})
    response = api_client.get(url)

    assert response.status_code == http.client.OK
    assert response.json()['id'] == str(public_profile.pk)


@pytest.mark.django_db
def test_company_profile_public_404_private_profile(private_profile, api_client):
    url = reverse('company-public-profile-detail', kwargs={'companies_house_number': private_profile.number})
    response = api_client.get(url)

    assert response.status_code == http.client.NOT_FOUND


@pytest.mark.django_db
def test_verify_company_with_code(authed_client, authed_supplier, settings):
    with mock.patch('requests.post'):
        company = models.Company.objects.create(
            **{
                'number': '11234567',
                'name': 'Test Company',
                'website': 'http://example.com',
                'description': 'Company description',
                'has_exported_before': True,
                'date_of_creation': '2010-10-10',
                'postal_full_name': 'test_full_name',
                'address_line_1': 'test_address_line_1',
                'address_line_2': 'test_address_line_2',
                'locality': 'test_locality',
                'postal_code': 'test_postal_code',
                'country': 'test_country',
            }
        )

    authed_supplier.company = company
    authed_supplier.save()

    company.refresh_from_db()
    assert company.verification_code

    url = reverse('company-verify')
    response = authed_client.post(url, {'code': company.verification_code}, format='json')

    assert response.status_code == http.client.OK

    company.refresh_from_db()
    assert company.verified_with_code is True


@pytest.mark.django_db
def test_verify_company_with_code_invalid_code(authed_client, authed_supplier, settings):
    with mock.patch('requests.post'):
        company = models.Company.objects.create(
            **{
                'number': '11234567',
                'name': 'Test Company',
                'website': 'http://example.com',
                'description': 'Company description',
                'has_exported_before': True,
                'date_of_creation': '2010-10-10',
                'postal_full_name': 'test_full_name',
                'address_line_1': 'test_address_line_1',
                'address_line_2': 'test_address_line_2',
                'locality': 'test_locality',
                'postal_code': 'test_postal_code',
                'country': 'test_country',
            }
        )

    authed_supplier.company = company
    authed_supplier.save()

    company.refresh_from_db()
    assert company.verification_code
    response = authed_client.post(reverse('company-verify'), {'code': 'invalid'}, format='json')

    assert response.status_code == http.client.BAD_REQUEST

    company.refresh_from_db()
    assert company.verified_with_code is False


search_urls = (
    reverse('investment-support-directory-search'),
    reverse('find-a-supplier-search'),
)


@pytest.mark.rebuild_elasticsearch
@pytest.mark.parametrize('url', search_urls)
@mock.patch('elasticsearch_dsl.response.Response.to_dict')
def test_search(mock_get_search_results, url, api_client):

    mock_get_search_results.return_value = expected_value = {
        'hits': {
            'total': 2,
            'hits': [None, None],
        },
    }
    data = {
        'term': 'bones',
        'page': 1,
        'size': 10,
        'sectors': [choices.INDUSTRIES[0][0]],
    }
    response = api_client.get(url, data=data)

    assert response.status_code == 200
    assert response.json() == expected_value


@pytest.mark.rebuild_elasticsearch
@pytest.mark.parametrize('url', search_urls)
@pytest.mark.parametrize(
    'page_number,expected_start',
    [
        [1, 0],
        [2, 5],
        [3, 10],
        [4, 15],
        [5, 20],
        [6, 25],
        [7, 30],
        [8, 35],
    ],
)
def test_search_paginate_first_page(url, page_number, expected_start, api_client, settings):
    es = connections.get_connection('default')
    with mock.patch.object(es, 'search', return_value={}) as mock_search:
        data = {'term': 'bones', 'page': page_number, 'size': 5}

        response = api_client.get(url, data=data)

        assert response.status_code == 200, response.content
        assert mock_search.call_count == 1
        assert mock_search.call_args[1]['body']['from'] == expected_start


@pytest.mark.rebuild_elasticsearch
@pytest.mark.parametrize('url', search_urls)
def test_search_sector_filter(url, api_client, settings):
    es = connections.get_connection('default')
    with mock.patch.object(es, 'search', return_value={}):
        data = {
            'term': 'bees',
            'sectors': [sectors.AEROSPACE],
            'size': 5,
            'page': 1,
        }
        response = api_client.get(url, data=data)

        assert response.status_code == 200, response.content


@pytest.mark.rebuild_elasticsearch
@pytest.mark.parametrize('url', search_urls)
def test_search_wildcard_filters(url, api_client, settings):
    es = connections.get_connection('default')

    with mock.patch.object(es, 'search', return_value={}):
        data = {
            'term': 'bees',
            'expertise_industries': choices.INDUSTRIES[1][0],
            'expertise_regions': choices.EXPERTISE_REGION_CHOICES[1][0],
            'expertise_countries': choices.COUNTRY_CHOICES[1][0],
            'expertise_languages': choices.EXPERTISE_LANGUAGES[1][0],
            'expertise_products_services_labels': ['IT'],
            'size': 5,
            'page': 1,
        }
        response = api_client.get(url, data=data)
        assert response.status_code == 200, response.content


@pytest.mark.rebuild_elasticsearch
@pytest.mark.parametrize('url', search_urls)
def test_search_wildcard_filters_multiple(url, api_client, settings):
    es = connections.get_connection('default')

    with mock.patch.object(es, 'search', return_value={}):
        data = {
            'term': 'bees',
            'expertise_industries': [sectors.ADVANCED_MANUFACTURING, sectors.AIRPORTS],
            'expertise_products_services_labels': ['IT', 'REGULATION'],
            'size': 5,
            'page': 1,
        }
        response = api_client.get(url, data=data)

        assert response.status_code == 200, response.content


@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
@pytest.mark.parametrize('url', search_urls)
@pytest.mark.parametrize(
    'term,filter_name,filter_value ,expected',
    [
        # term
        ['Wolf', '', '', ['1']],
        ['Tongue', '', '', ['2']],
        ['common', '', '', ['1', '2', '3']],
        ['common', 'expertise_industries', [sectors.AEROSPACE], ['1', '2']],
        # expertise_industries
        ['', 'expertise_industries', [sectors.AEROSPACE], ['1', '2']],
        [
            '',
            'expertise_industries',
            [sectors.AEROSPACE, sectors.AIRPORTS],
            ['1', '2', '3'],
        ],
        # expertise_industries via q
        [sectors.AEROSPACE, '', '', ['1', '2']],
        # expertise_products_services_labels via q
        ['Regulatory', '', '', ['1', '2', '3']],
        ['', 'expertise_industries', [sectors.AEROSPACE, sectors.AIRPORTS], ['1', '2', '3']],
        # expertise_regions
        ['', 'expertise_regions', [choices.EXPERTISE_REGION_CHOICES[4][0]], ['1', '2']],
        [
            '',
            'expertise_regions',
            [
                choices.EXPERTISE_REGION_CHOICES[4][0],
                choices.EXPERTISE_REGION_CHOICES[5][0],
            ],
            ['1', '2', '3'],
        ],
        # expertise_languages
        [
            '',
            'expertise_languages',
            [choices.EXPERTISE_LANGUAGES[0][0]],
            ['1', '2'],
        ],
        [
            '',
            'expertise_languages',
            [choices.EXPERTISE_LANGUAGES[0][0], choices.EXPERTISE_LANGUAGES[2][0]],
            ['1', '2', '3'],
        ],
        # expertise_countries
        ['', 'expertise_countries', [choices.COUNTRY_CHOICES[23][0]], ['1', '2']],
        ['', 'expertise_countries', [choices.COUNTRY_CHOICES[23][0], choices.COUNTRY_CHOICES[24][0]], ['1', '2', '3']],
        # expertise_products_services
        ['', 'expertise_products_services_labels', ['Finance'], ['1', '2']],
        ['', 'expertise_products_services_labels', ['Finance', 'IT'], ['1', '2', '3']],
    ],
)
def test_search_results(url, term, filter_name, filter_value, expected, search_data, api_client):
    data = {
        'term': term,
        'page': '1',
        'size': '5',
        filter_name: filter_value,
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200

    hits = response.json()['hits']['hits']

    assert len(hits) == len(expected)
    for hit in hits:
        assert hit['_id'] in expected


@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
@pytest.mark.parametrize('url', search_urls)
@pytest.mark.parametrize('stop_term', ['limited', 'plc', 'ltd'])
def test_search_results_stopwords(url, stop_term, search_companies_stopwords, api_client):
    data = {
        'term': 'mycompany {stop_term}',
        'page': '1',
        'size': '5',
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200

    hits = response.json()['hits']['hits']
    assert len(hits) == 1
    assert hits[0]['_id'] == '1'


@pytest.mark.parametrize('url', search_urls)
@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
@pytest.mark.parametrize(
    'term, expected',
    [
        [sectors.AEROSPACE, ['1', '2']],
        [choices.COUNTRY_CHOICES[23][0], ['1', '2']],
        [choices.EXPERTISE_REGION_CHOICES[4][0], ['1', '2']],
        [choices.EXPERTISE_LANGUAGES[0][0], ['1', '2']],
    ],
)
def test_search_term_expertise(url, term, expected, search_data, api_client):

    data = {
        'term': term,
        'page': '1',
        'size': '5',
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200

    hits = response.json()['hits']['hits']

    assert len(hits) == len(expected)
    for hit in hits:
        assert hit['_id'] in expected


@pytest.mark.parametrize('url', search_urls)
@pytest.mark.parametrize(
    'filters,expected',
    [
        (
            {
                'expertise_industries': [sectors.AEROSPACE, sectors.AIRPORTS],
                'expertise_regions': ['NORTH_EAST', 'NORTH_WEST'],
                'expertise_countries': [
                    'AF',  # Afghanistan
                    'AL',  # Albania
                ],
                'expertise_languages': [
                    'ab',  # Abkhazian
                    'aa',  # Afar
                ],
                'expertise_products_services_labels': [
                    'Accounting and tax',  # from financial filter
                    'Business development',  # from management consulting filter
                ],
            },
            ['1', '2'],
        ),
        (
            {
                'expertise_industries': [sectors.AEROSPACE, sectors.AIRPORTS],
                'expertise_regions': ['NORTH_EAST', 'NORTH_WEST'],
                'expertise_languages': [
                    'ab',  # Abkhazian
                    'aa',  # Afar
                ],
                'expertise_products_services_labels': [
                    'Accounting and tax',  # from financial filter
                    'Business development',  # from management consulting filter
                ],
            },
            ['1', '2', '4'],
        ),
        (
            {
                'expertise_industries': [sectors.AEROSPACE, sectors.AIRPORTS],
                'expertise_languages': [
                    'ab',  # Abkhazian
                    'aa',  # Afar
                ],
                'expertise_products_services_labels': [
                    'Accounting and tax',  # from financial filter
                    'Business development',  # from management consulting filter
                ],
            },
            ['1', '2', '4', '6'],
        ),
        (
            {
                'expertise_industries': [sectors.AEROSPACE, sectors.AIRPORTS],
                'expertise_languages': [
                    'ab',  # Abkhazian
                    'aa',  # Afar
                ],
            },
            ['1', '2', '3', '4', '6'],
        ),
        ({'expertise_industries': [sectors.AEROSPACE, sectors.AIRPORTS]}, ['1', '2', '3', '4', '5', '6']),
        ({}, ['1', '2', '3', '4', '5', '6', '7']),
    ],
)
@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
def test_search_filter_and_or(url, filters, expected, api_client, search_data_and_or):
    data = {
        **filters,
        'term': 'wolf',
        'page': '1',
        'size': '10',
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200, response.json()

    actual = [hit['_id'] for hit in response.json()['hits']['hits']]

    assert sorted(actual) == expected


@pytest.mark.parametrize('url', search_urls)
@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
def test_search_filter_and_or_single(url, api_client, settings):
    factories.CompanyFactory(
        name='Wolf limited',
        is_published_investment_support_directory=True,
        expertise_products_services={
            'Legal': ['Company incorporation', 'Employment', 'Immigration'],
            'Human Resources': ['Staff onboarding', 'Employment and talent research'],
            'Business Support': ['Business relocation', 'Staff and family relocation'],
            'Management Consulting': ['Workforce development', 'Strategy and long-term planning'],
        },
        expertise_languages=['en,', 'zh', 'fr', 'es', 'pa', 'hi', 'pt', 'ar'],
        expertise_countries=['CN', 'IN', 'PK', 'US', 'ZA', 'EG', 'BR'],
        expertise_regions=[
            'WALES',
            'NORTH_EAST',
            'NORTH_WEST',
            'YORKSHIRE_AND_HUMBER',
            'EAST_MIDLANDS',
            'WEST_MIDLANDS',
            'EASTERN',
            'LONDON',
            'SOUTH_EAST',
            'SOUTH_WEST',
        ],
        expertise_industries=[
            'Advanced manufacturing',
            'Aerospace',
            'Automotive',
            'Creative and media',
            'Education and training',
            'Food and drink',
            'Healthcare and medical',
            'Software and computer services',
            'Retail and luxury',
        ],
        id=1,
    )
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()

    data = {
        'expertise_regions': ['NORTH_EAST'],
        'expertise_languages': ['es'],
        'expertise_products_services_labels': ['Accounting and tax', 'Regulatory support'],
        'page': '1',
        'size': '10',
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200, response.json()

    actual = [hit['_id'] for hit in response.json()['hits']['hits']]
    assert actual == []


@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
@pytest.mark.parametrize('url', search_urls)
def test_search_filter_partial_match(url, api_client, settings):
    factories.CompanyFactory(
        name='Wolf limited',
        is_published_investment_support_directory=True,
        expertise_products_services={
            'Legal': ['Company incorporation', 'Immigration'],
            'Human Resources': ['Staff onboarding', 'Employment and talent research'],
            'Business Support': ['Business relocation', 'Staff and family relocation'],
            'Management Consulting': ['Workforce development', 'Strategy and long-term planning'],
        },
        expertise_languages=['en,', 'zh', 'fr', 'es', 'pa', 'hi', 'pt', 'ar'],
        expertise_countries=['CN', 'IN', 'PK', 'US', 'ZA', 'EG', 'BR'],
        expertise_regions=[
            'WALES',
            'NORTH_EAST',
            'NORTH_WEST',
            'YORKSHIRE_AND_HUMBER',
            'EAST_MIDLANDS',
            'WEST_MIDLANDS',
            'EASTERN',
            'LONDON',
            'SOUTH_EAST',
            'SOUTH_WEST',
        ],
        expertise_industries=[
            'Advanced manufacturing',
            'Aerospace',
            'Automotive',
            'Creative and media',
            'Education and training',
            'Food and drink',
            'Healthcare and medical',
            'Software and computer services',
            'Retail and luxury',
        ],
        id=1,
    )
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()

    data = {
        'expertise_regions': ['NORTH_EAST'],
        'expertise_languages': ['es'],
        'expertise_products_services_labels': [
            'Employment',
        ],
        'page': '1',
        'size': '10',
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200, response.json()

    actual = [hit['_id'] for hit in response.json()['hits']['hits']]
    assert actual == []


@pytest.mark.parametrize('url', search_urls)
@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
def test_search_order_sibling_filters(url, api_client, settings):
    ordering_values = {**default_ordering_values}
    del ordering_values['expertise_regions']

    factories.CompanyFactory(
        **ordering_values,
        name='Wolf limited',
        expertise_regions=['NORTH_EAST'],
        id=1,
    )
    factories.CompanyFactory(
        **ordering_values,
        name='Wolf corp',
        expertise_regions=['NORTH_WEST', 'NORTH_EAST'],
        id=2,
    )
    factories.CompanyFactory(
        **ordering_values,
        name='Wolf land',
        expertise_regions=['NORTH_WEST'],
        id=3,
    )
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()

    data = {
        'expertise_regions': ['NORTH_WEST', 'NORTH_EAST'],
        'term': 'wolf',
        'page': '1',
        'size': '10',
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200, response.json()

    actual = [hit['_id'] for hit in response.json()['hits']['hits']]

    assert actual == ['2', '3', '1']


@pytest.mark.parametrize('url', search_urls)
@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
def test_search_order_search_term(url, api_client, settings):
    factories.CompanyFactory(
        **default_ordering_values,
        name='Wolf limited',
        summary='Providing wind energy',
        id=1,
    )
    factories.CompanyFactory(
        **default_ordering_values,
        name='Wolf corp',
        summary='Wind and energy',
        id=2,
    )
    factories.CompanyFactory(
        **default_ordering_values,
        name='Wolf land',
        summary='Energy and wind',
        id=3,
    )
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()

    data = {
        'term': 'wind energy',
        'page': '1',
        'size': '10',
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200, response.json()

    actual = [hit['_id'] for hit in response.json()['hits']['hits']]

    assert actual == ['1', '2', '3']


@pytest.mark.parametrize('url', search_urls)
@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
def test_search_order_case_study(url, api_client, settings):
    company_one = factories.CompanyFactory(
        **default_ordering_values,
        name='Wolf limited',
        summary='Providing wind energy',
        id=1,
    )
    company_two = factories.CompanyFactory(
        **default_ordering_values,
        name='Wolf corp',
        id=2,
    )
    company_three = factories.CompanyFactory(
        **default_ordering_values,
        name='Wolf land',
        id=3,
    )
    factories.CompanyCaseStudyFactory(
        description='',
        company=company_one,
        title='Providing wind energy',
    )

    factories.CompanyCaseStudyFactory(
        description='',
        company=company_two,
        title='Wind and energy',
    )
    factories.CompanyCaseStudyFactory(
        description='',
        company=company_three,
        title='Energy and wind',
    )
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()
    data = {
        'term': 'wind energy',
        'page': '1',
        'size': '10',
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200, response.json()

    actual = [hit['_id'] for hit in response.json()['hits']['hits']]

    assert actual == ['1', '2', '3']


@pytest.mark.parametrize('url', search_urls)
@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
def test_search_american_english_full_words(url, api_client, settings):
    factories.CompanyFactory(
        **default_ordering_values,
        name='Wolf limited',
        summary='Colour and palour or draught beer',
        id=1,
    )
    factories.CompanyFactory(
        **default_ordering_values,
        name='Wolf limited',
        summary='Colour of draught magic',
        id=2,
    )
    factories.CompanyFactory(
        **default_ordering_values,
        name='Wolf r us',
        summary='Colourful gremlins',
        id=3,
    )
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()
    data = {
        'term': 'colorful draft',
        'page': '1',
        'size': '10',
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200, response.json()

    actual = [hit['_id'] for hit in response.json()['hits']['hits']]

    assert set(actual) == {'1', '2', '3'}


@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
@pytest.mark.parametrize('url', search_urls)
def test_search_american_english_synonyms(url, api_client, settings):
    factories.CompanyFactory(
        **default_ordering_values,
        name='Car bonnet',
        id=1,
    )
    factories.CompanyFactory(
        **default_ordering_values,
        name='Wolf r us',
        summary='Colourful gremlins',
        id=3,
    )
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()
    data = {
        'term': 'car hood',
        'page': '1',
        'size': '10',
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200, response.json()

    actual = [hit['_id'] for hit in response.json()['hits']['hits']]

    assert actual == ['1']


@pytest.mark.django_db
@pytest.mark.rebuild_elasticsearch
@pytest.mark.parametrize('url', search_urls)
def test_search_results_highlight(url, search_highlighting_data, api_client):
    data = {
        'term': 'power',
        'page': 1,
        'size': 5,
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200
    results = response.json()
    hits = results['hits']['hits']

    assert hits[0]['highlight'] == {'description': ['Providing the <em>power</em> and beauty of Aardvarks.']}


@pytest.mark.django_db
@pytest.mark.rebuild_elasticsearch
@pytest.mark.parametrize('url', search_urls)
def test_search_results_highlight_long(
    url,
    search_highlighting_data,
    api_client,
):
    data = {
        'term': 'wolf',
        'page': 1,
        'size': 5,
    }

    response = api_client.get(url, data=data)

    assert response.status_code == 200
    results = response.json()
    hits = results['hits']['hits']

    assert hits[0]['highlight']['description'] == [
        'This is a very long thing about <em>wolf</em> stuff.',
        'The <em>wolf</em> cries at night.',
    ]


@pytest.mark.django_db
def test_verify_companies_house_missing_access_token(authed_client, authed_supplier):
    url = reverse('company-verify-companies-house')
    response = authed_client.post(url)  # missing access_token

    assert response.status_code == 400
    assert response.json() == {'access_token': ['This field is required.']}
    company = authed_supplier.company
    company.refresh_from_db()
    assert company.verified_with_companies_house_oauth2 is False


@pytest.mark.django_db
def test_verify_companies_house_invalid_access_token(
    companies_house_oauth_invalid_access_token, authed_client, authed_supplier
):
    serializer = serializers.VerifyCompanyWithCompaniesHouseSerializer
    url = reverse('company-verify-companies-house')
    response = authed_client.post(url, {'access_token': '123'})

    assert response.status_code == 400
    assert response.json() == {'access_token': [serializer.MESSAGE_BAD_ACCESS_TOKEN]}
    company = authed_supplier.company
    company.refresh_from_db()
    assert company.verified_with_companies_house_oauth2 is False


@pytest.mark.django_db
def test_verify_companies_house_wrong_company_access_token(
    companies_house_oauth_wrong_company, authed_client, authed_supplier
):
    serializer = serializers.VerifyCompanyWithCompaniesHouseSerializer
    url = reverse('company-verify-companies-house')
    response = authed_client.post(url, {'access_token': '123'})

    assert response.status_code == 400
    assert response.json() == {'access_token': [serializer.MESSAGE_SCOPE_ERROR]}
    company = authed_supplier.company
    company.refresh_from_db()
    assert company.verified_with_companies_house_oauth2 is False


@pytest.mark.django_db
def test_verify_companies_house_expired_access_token(
    companies_house_oauth_expired_token, authed_client, authed_supplier
):
    serializer = serializers.VerifyCompanyWithCompaniesHouseSerializer
    url = reverse('company-verify-companies-house')
    response = authed_client.post(url, {'access_token': '123'})

    assert response.status_code == 400
    assert response.json() == {'access_token': [serializer.MESSAGE_EXPIRED]}
    company = authed_supplier.company
    company.refresh_from_db()
    assert company.verified_with_companies_house_oauth2 is False


@pytest.mark.django_db
def test_verify_companies_house_good_access_token(
    companies_house_oauth_valid_token, authed_supplier, authed_client, mock_elasticsearch_company_save
):
    url = reverse('company-verify-companies-house')
    response = authed_client.post(url, {'access_token': '123'})

    assert response.status_code == 200
    company = authed_supplier.company
    company.refresh_from_db()
    assert company.verified_with_companies_house_oauth2 is True


@pytest.mark.django_db
def test_remove_collaborators(authed_client, authed_supplier):
    authed_supplier.role = user_roles.ADMIN
    authed_supplier.save()

    company_user_one = factories.CompanyUserFactory(company=authed_supplier.company, role=user_roles.EDITOR)
    company_user_two = factories.CompanyUserFactory(company=authed_supplier.company, role=user_roles.EDITOR)
    company_user_three = factories.CompanyUserFactory(company=authed_supplier.company, role=user_roles.EDITOR)
    company_user_four = factories.CompanyUserFactory(role=user_roles.EDITOR)

    company_users = authed_supplier.company.company_users.all()
    assert company_user_one in company_users
    assert company_user_two in company_users
    assert company_user_three in company_users
    assert company_user_four not in company_users
    assert authed_supplier in company_users

    url = reverse('remove-collaborators')
    data = {'sso_ids': [company_user_one.sso_id, company_user_two.sso_id]}
    response = authed_client.post(url, data=data)

    assert response.status_code == 200

    company_users = company_users = authed_supplier.company.company_users.all()

    assert company_user_one not in company_users
    assert company_user_two not in company_users
    assert company_user_three in company_users
    assert company_user_four not in company_users
    assert authed_supplier in company_users


@pytest.mark.django_db
def test_remove_collaborators_cannot_remove_self(authed_client, authed_supplier):
    factories.CompanyUserFactory(company=authed_supplier.company, role=user_roles.ADMIN)
    authed_supplier.role = user_roles.ADMIN
    authed_supplier.save()

    assert authed_supplier in authed_supplier.company.company_users.all()

    url = reverse('remove-collaborators')
    data = {'sso_ids': [authed_supplier.sso_id]}
    response = authed_client.post(url, data=data)

    assert response.status_code == 200
    assert authed_supplier in authed_supplier.company.company_users.all()


@pytest.mark.django_db
def test_multi_user_account_management_views_forbidden(authed_client, authed_supplier):
    url = reverse('remove-collaborators')
    authed_supplier.role = user_roles.EDITOR
    authed_supplier.save()

    response = authed_client.post(url, {})

    assert response.status_code == 403


@pytest.mark.django_db
def test_collaboration_request_create(authed_supplier, authed_client):

    url = reverse('collaborator-request')
    data = {
        'role': user_roles.ADMIN,
    }
    response = authed_client.post(url, data, format='json')
    assert response.status_code == 201
    collaboration_request = models.CollaborationRequest.objects.get(requestor=authed_supplier)
    assert collaboration_request.name == authed_supplier.name
    assert collaboration_request.role == user_roles.ADMIN
    assert collaboration_request.accepted is False
    assert collaboration_request.accepted_date is None


@pytest.mark.django_db
def test_collaboration_request_list(authed_supplier, authed_client):
    collaboration_request = factories.CollaborationRequestFactory(requestor=authed_supplier)
    factories.CollaborationRequestFactory()
    response = authed_client.get(reverse('collaborator-request'))
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'uuid': str(collaboration_request.uuid),
            'requestor': collaboration_request.requestor.id,
            'requestor_sso_id': collaboration_request.requestor.sso_id,
            'name': collaboration_request.name,
            'role': collaboration_request.role,
            'accepted': False,
            'accepted_date': None,
        }
    ]


@pytest.mark.django_db
def test_collaboration_request_delete(authed_supplier, authed_client):
    requestor = factories.CompanyUserFactory(company=authed_supplier.company)
    collaboration_request = factories.CollaborationRequestFactory(requestor=requestor)
    pk = collaboration_request.uuid

    url = reverse('collaborator-request-detail', kwargs={'uuid': pk})
    response = authed_client.delete(url)

    assert response.status_code == http.client.NO_CONTENT
    assert models.CollaborationRequest.objects.filter(pk=pk).exists() is False


@freeze_time('2016-11-23T11:21:10.977518Z')
@pytest.mark.django_db
def test_collaboration_request_update(authed_supplier, authed_client):
    requestor = factories.CompanyUserFactory(role=user_roles.MEMBER, company=authed_supplier.company)
    collaboration_request = factories.CollaborationRequestFactory(requestor=requestor, role=user_roles.ADMIN)

    url = reverse('collaborator-request-detail', kwargs={'uuid': collaboration_request.uuid})
    response = authed_client.patch(url, data={'accepted': True})
    assert response.status_code == status.HTTP_200_OK
    data = {
        'uuid': str(collaboration_request.uuid),
        'requestor': collaboration_request.requestor.id,
        'requestor_sso_id': collaboration_request.requestor.sso_id,
        'name': collaboration_request.name,
        'role': collaboration_request.role,
        'accepted': True,
        'accepted_date': '2016-11-23T11:21:10.977518Z',
    }
    assert response.json() == data

    requestor.refresh_from_db()
    assert requestor.role == user_roles.ADMIN


@pytest.mark.django_db
def test_collaboration_request_update_different_company(authed_client):
    collaboration_request = factories.CollaborationRequestFactory()

    url = reverse('collaborator-request-detail', kwargs={'uuid': collaboration_request.uuid})
    response = authed_client.patch(url, data={'accepted': True})

    assert response.status_code == 404


@pytest.mark.django_db
@mock.patch.object(helpers, 'send_request_identity_verification_message')
def test_request_identity_verification(mock_send_request_identity_message, authed_client, authed_supplier):
    url = reverse('company-verify-identity')

    response = authed_client.post(url)

    assert response.status_code == 200
    assert mock_send_request_identity_message.call_count == 1
    assert mock_send_request_identity_message.call_args == mock.call(authed_supplier)


@pytest.mark.django_db
def test_add_collaborator_view(authed_client):
    company = factories.CompanyFactory(
        name='Test Company',
        date_of_creation=datetime.date(2000, 10, 10),
    )
    data = {
        'sso_id': 300,
        'name': 'Abc',
        'company': company.number,
        'company_email': 'abc@def.com',
        'mobile_number': '9876543210',
    }

    url = reverse('register-company-collaborator-request')
    response = authed_client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {**data, 'role': user_roles.ADMIN}


@pytest.mark.django_db
def test_collaboration_invite_create(authed_client, authed_supplier):
    data = {'collaborator_email': 'jim@example.com', 'role': user_roles.ADMIN}

    url = reverse('collaboration-invite')
    response = authed_client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED, response.json()
    assert response.json() == {
        'uuid': mock.ANY,
        'collaborator_email': data['collaborator_email'],
        'company': authed_supplier.company.pk,
        'company_user': authed_supplier.pk,
        'accepted_date': None,
        'role': data['role'],
        'accepted': False,
    }


@pytest.mark.django_db
def test_collaboration_invite_list(authed_client, authed_supplier):
    factories.CollaborationInviteFactory()  # expect this to not be in the response as it's for a different company
    invite = factories.CollaborationInviteFactory(company=authed_supplier.company)

    url = reverse('collaboration-invite')
    response = authed_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [
        {
            'uuid': str(invite.uuid),
            'collaborator_email': invite.collaborator_email,
            'company': invite.company.pk,
            'company_user': invite.company_user.pk,
            'accepted_date': invite.accepted_date,
            'role': invite.role,
            'accepted': False,
        }
    ]


@pytest.mark.django_db
def test_collaboration_invite_retrieve(client, authed_supplier):
    invite = factories.CollaborationInviteFactory(company=authed_supplier.company)

    url = reverse('collaboration-invite-detail', kwargs={'uuid': invite.uuid})
    response = client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'uuid': str(invite.uuid),
        'collaborator_email': invite.collaborator_email,
        'company': invite.company.pk,
        'company_user': invite.company_user.pk,
        'accepted_date': invite.accepted_date,
        'role': invite.role,
        'accepted': False,
    }


@pytest.mark.django_db
def test_collaboration_invite_update(authed_client, authed_supplier):
    # at this point the user's supplier has not yet been created
    authed_supplier.delete()
    invite = factories.CollaborationInviteFactory(company=authed_supplier.company)
    url = reverse('collaboration-invite-detail', kwargs={'uuid': invite.uuid})
    response = authed_client.patch(url, data={'accepted': True})

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'uuid': str(invite.uuid),
        'collaborator_email': invite.collaborator_email,
        'company': invite.company.pk,
        'company_user': invite.company_user.pk,
        'accepted_date': mock.ANY,
        'role': invite.role,
        'accepted': True,
    }
    company_user = models.CompanyUser.objects.get(company_email=invite.collaborator_email)
    assert company_user.company == invite.company
    assert company_user.role == invite.role
    assert company_user.name == 'supplier1 bloggs'


@pytest.mark.django_db
def test_collaboration_invite_delete(authed_client, authed_supplier):
    invite = factories.CollaborationInviteFactory(company=authed_supplier.company)

    url = reverse('collaboration-invite-detail', kwargs={'uuid': invite.uuid})
    response = authed_client.delete(url)

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
@pytest.mark.parametrize('role', (user_roles.ADMIN, user_roles.EDITOR, user_roles.MEMBER))
def test_change_collaborator_role(authed_client, authed_supplier, role):
    company_user = factories.CompanyUserFactory(company=authed_supplier.company, role=user_roles.EDITOR)

    url = reverse('change-collaborator-role', kwargs={'sso_id': company_user.sso_id})

    response = authed_client.patch(url, {'role': role})

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['role'] == role
    company_user.refresh_from_db()
    assert company_user.role == role


@pytest.mark.django_db
def test_change_collaborator_role_wrong_company(authed_client, authed_supplier):
    company_user = factories.CompanyUserFactory(role=user_roles.EDITOR)

    url = reverse('change-collaborator-role', kwargs={'sso_id': company_user.sso_id})

    response = authed_client.patch(url, {'role': user_roles.ADMIN})

    assert response.status_code == status.HTTP_404_NOT_FOUND


# DELTE?
@pytest.fixture
def company_user():
    return factories.CompanyUserFactory(
        company_email='jim@example.com',
        company__number='01234567',
        company__name='foo ltd',
        company__sectors=['AEROSPACE'],
        name='Jim Example',
        sso_id=123,
        company__export_status='YES',
        company__has_exported_before=True,
    )


@pytest.mark.django_db
def test_company_user_retrieve(authed_client, authed_supplier):
    response = authed_client.get(reverse('supplier'))

    expected = serializers.CompanyUserSerializer(authed_supplier).data

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
def test_company_user_update(authed_client, authed_supplier):
    response = authed_client.patch(reverse('supplier'), {'company_email': 'a@b.co'}, format='json')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['company_email'] == 'a@b.co'


@pytest.mark.django_db
def test_company_user_retrieve_no_company_user(authed_client, authed_supplier):
    authed_supplier.delete()

    response = authed_client.get(reverse('supplier'))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_gecko_num_registered_company_user_view_returns_correct_json():
    client = APIClient()
    models.CompanyUser.objects.create(**VALID_SUPPLIER_REQUEST_DATA)
    # Use basic auth with user=gecko and pass=X
    encoded_creds = base64.b64encode('gecko:X'.encode('ascii')).decode("ascii")
    client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded_creds)

    response = client.get(reverse('gecko-total-registered-suppliers'))

    expected = {"item": [{"value": 1, "text": "Total registered company users"}]}
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
def test_gecko_num_registered_company_user_view_requires_auth():
    client = APIClient()

    response = client.get(reverse('gecko-total-registered-suppliers'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_gecko_num_registered_company_user_view_rejects_incorrect_creds():
    client = APIClient()
    # correct creds are gecko:X
    encoded_creds = base64.b64encode('user:pass'.encode('ascii')).decode("ascii")
    client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded_creds)

    response = client.get(reverse('gecko-total-registered-suppliers'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@mock.patch('core.tasks.send_email')
def test_unsubscribe_company_user(mock_task, authed_client, authed_supplier):
    response = authed_client.post(reverse('unsubscribe-supplier'))

    authed_supplier.refresh_from_db()
    assert response.status_code == 200
    assert authed_supplier.unsubscribed is True
    assert mock_task.delay.called


@pytest.mark.django_db
@mock.patch('notifications.notifications.company_user_unsubscribed')
def test_unsubscribe_company_user_email_confirmation(mock_company_user_unsubscribed, authed_client, authed_supplier):
    authed_client.post(reverse('unsubscribe-supplier'))

    mock_company_user_unsubscribed.assert_called_once_with(company_user=authed_supplier)


@pytest.mark.django_db
@mock.patch('core.authentication.Oauth2AuthenticationSSO.authenticate_credentials')
def test_external_company_user_details_get_bearer_auth(
    mock_authenticate_credentials, client, authed_supplier, settings
):
    sso_user = SSOUser(id=authed_supplier.sso_id, email='test@example.com')
    mock_authenticate_credentials.return_value = (sso_user, '123')

    settings.FAS_COMPANY_PROFILE_URL = 'http://profile/{number}'
    expected = serializers.ExternalCompanyUserSerializer(authed_supplier).data

    url = reverse('external-supplier-details')
    response = client.get(url, {}, HTTP_AUTHORIZATION='Bearer 123')

    assert response.status_code == 200
    assert response.json() == expected
    assert mock_authenticate_credentials.call_count == 1
    assert mock_authenticate_credentials.call_args == mock.call('123')


@pytest.mark.django_db
def test_external_company_user_details_get_sso_auth(authed_client, authed_supplier, settings):
    settings.FAS_COMPANY_PROFILE_URL = 'http://profile/{number}'
    expected = serializers.ExternalCompanyUserSerializer(authed_supplier).data

    url = reverse('external-supplier-details')
    response = authed_client.get(url, {})

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.django_db
def test_external_company_user_details_post(authed_client):
    response = authed_client.post(reverse('external-supplier-details'), {}, HTTP_AUTHORIZATION='Bearer 123')

    assert response.status_code == 405


@pytest.mark.django_db
def test_external_company_user_details_get_no_supplier(authed_client, authed_supplier):
    authed_supplier.delete()

    response = authed_client.get(reverse('external-supplier-details'), {}, HTTP_AUTHORIZATION='Bearer 123')

    assert response.status_code == 404


@pytest.mark.django_db
def test_external_company_user_sso_list(authed_client, authed_supplier):

    company_users = factories.CompanyUserFactory.create_batch(3)
    url = reverse('external-supplier-sso-list')
    response = authed_client.get(url)

    assert response.status_code == 200
    assert response.json() == [
        company_users[2].sso_id,
        company_users[1].sso_id,
        company_users[0].sso_id,
        authed_supplier.sso_id,
    ]


@pytest.mark.django_db
def test_company_collaborators_anon_users():
    url = reverse('supplier-company-collaborators-list')
    client = APIClient()

    response = client.get(url)

    assert response.status_code == 401


@pytest.mark.django_db
def test_company_collaborators_not_profile_owner(authed_supplier, authed_client):
    authed_supplier.role = user_roles.EDITOR
    authed_supplier.save()

    url = reverse('supplier-company-collaborators-list')

    response = authed_client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_company_collaborators_profile_owner(authed_supplier, authed_client):
    authed_supplier.role = user_roles.ADMIN
    authed_supplier.save()

    company_user_one = factories.CompanyUserFactory(company=authed_supplier.company, role=user_roles.EDITOR)
    company_user_two = factories.CompanyUserFactory(company=authed_supplier.company, role=user_roles.EDITOR)
    factories.CompanyUserFactory()

    url = reverse('supplier-company-collaborators-list')

    response = authed_client.get(url)

    assert response.status_code == 200
    parsed = response.json()
    company_user_sso_ids = {company_user_one.sso_id, company_user_two.sso_id, authed_supplier.sso_id}

    assert {company_user['sso_id'] for company_user in parsed} == company_user_sso_ids


@pytest.mark.django_db
def test_company_collaborators_profile_owner_collaborators(authed_supplier, authed_client):
    authed_supplier.role = user_roles.ADMIN
    authed_supplier.save()

    url = reverse('supplier-company-collaborators-list')

    response = authed_client.get(url)

    assert response.status_code == 200
    assert response.json() == [serializers.CompanyUserSerializer(authed_supplier).data]


@pytest.mark.django_db
@mock.patch('sigauth.helpers.RequestSignatureChecker.test_signature', mock.Mock(return_value=True))
@mock.patch('core.views.get_file_from_s3')
def test_company_user_csv_dump(mocked_get_file_from_s3, authed_client):
    settings.STORAGE_CLASS_NAME = 'default'
    settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE = 'my_db_buket'
    reload_module('company.views')
    reload_module('buyer.views')
    reload_urlconf()

    mocked_body = mock.Mock()
    mocked_body.read.return_value = b'company_name\r\nacme\r\n'
    mocked_get_file_from_s3.return_value = {'Body': mocked_body}
    response = authed_client.get(reverse('supplier-csv-dump'), {'token': settings.CSV_DUMP_AUTH_TOKEN})
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b'company_name\r\nacme\r\n'
    assert response._headers['content-type'] == ('Content-Type', 'text/csv')
    assert response._headers['content-disposition'] == (
        'Content-Disposition',
        'attachment; filename="{filename}"'.format(filename=settings.SUPPLIERS_CSV_FILE_NAME),
    )


@pytest.mark.django_db
def test_disconnect_company_user_sole_admin(authed_supplier, authed_client):
    authed_supplier.role = user_roles.ADMIN
    authed_supplier.save()

    url = reverse('company-disconnect-supplier')

    response = authed_client.post(url)

    assert response.status_code == 400
    assert response.json() == [helpers.MESSAGE_ADMIN_NEEDED]


@pytest.mark.parametrize('role', (user_roles.ADMIN, user_roles.EDITOR, user_roles.MEMBER))
@pytest.mark.django_db
def test_disconnect_company_user_multiple_admin(authed_supplier, authed_client, role):
    authed_supplier.role = role
    authed_supplier.save()
    factories.CompanyUserFactory(role=user_roles.ADMIN, company=authed_supplier.company)

    url = reverse('company-disconnect-supplier')

    response = authed_client.post(url)

    assert response.status_code == 200

    authed_supplier.refresh_from_db()

    assert authed_supplier.company is None
    assert authed_supplier.role == user_roles.MEMBER


@pytest.mark.django_db
def test_company_user_retrieve_sso_id(client):

    company_user = factories.CompanyUserFactory()

    url = reverse('supplier-retrieve-sso-id', kwargs={'sso_id': company_user.sso_id})

    response = client.get(url)

    assert response.json()['sso_id'] == company_user.sso_id


@pytest.mark.django_db
def test_company_delete_endpoint_signal_user(authed_client, authed_supplier):
    response = authed_client.delete(
        reverse(
            'company-delete-by-sso-id',
            kwargs={'sso_id': authed_supplier.sso_id, 'request_key': settings.DIRECTORY_SSO_API_SECRET},
        )
    )
    assert response.status_code == 204


@pytest.mark.django_db
def test_company_delete_endpoint_multiple_users(authed_client, authed_supplier):
    authed_supplier.role = user_roles.ADMIN
    authed_supplier.save()

    company_user_one = factories.CompanyUserFactory(company=authed_supplier.company, role=user_roles.EDITOR)
    company_user_two = factories.CompanyUserFactory(company=authed_supplier.company, role=user_roles.EDITOR)
    factories.CompanyUserFactory()

    assert authed_supplier.company.company_users.all().count() == 3

    response = authed_client.delete(
        reverse(
            'company-delete-by-sso-id',
            kwargs={'sso_id': authed_supplier.sso_id, 'request_key': settings.DIRECTORY_SSO_API_SECRET},
        )
    )
    assert response.status_code == 204

    company_user_one.refresh_from_db()
    company_user_two.refresh_from_db()
    authed_supplier.company.refresh_from_db()

    assert company_user_one.role == user_roles.ADMIN
    assert company_user_two.role == user_roles.ADMIN

    assert authed_supplier.company.company_users.all().count() == 2

    # check company is not deleted
    assert authed_supplier is not None


@pytest.mark.django_db
def test_company_delete_endpoint_for_random_user(authed_client):
    response = authed_client.delete(
        reverse('company-delete-by-sso-id', kwargs={'sso_id': 999, 'request_key': settings.DIRECTORY_SSO_API_SECRET})
    )
    assert response.status_code == 204


@pytest.mark.django_db
def test_company_delete_endpoint_for_random_request_key(authed_client):
    response = authed_client.delete(
        reverse('company-delete-by-sso-id', kwargs={'sso_id': 999, 'request_key': 'Random'})
    )
    assert response.status_code == 401


@pytest.mark.django_db
def test_company_delete_endpoint_for_user_not_associated_with_company(authed_client, authed_supplier):
    non_company_user = factories.CompanyUserFactory(company=None)
    user_before_delete_count = models.CompanyUser.objects.filter(sso_id=non_company_user.sso_id).count()

    assert user_before_delete_count == 1

    response = authed_client.delete(
        reverse(
            'company-delete-by-sso-id',
            kwargs={'sso_id': non_company_user.sso_id, 'request_key': settings.DIRECTORY_SSO_API_SECRET},
        )
    )

    assert response.status_code == 204
    user_after_delete_count = models.CompanyUser.objects.filter(sso_id=non_company_user.sso_id).count()
    assert user_after_delete_count == 0
