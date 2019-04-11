import datetime
import http
import uuid
from io import BytesIO
from unittest.mock import call, patch, Mock

from django.core.urlresolvers import reverse

from directory_constants.constants import choices, sectors
from elasticsearch_dsl import Index
from elasticsearch_dsl.connections import connections
import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image, ImageDraw

from company import helpers, models, serializers, views
from company.tests import (
    MockInvalidSerializer,
    MockValidSerializer,
    VALID_REQUEST_DATA,
)
from company.tests import factories
from supplier.tests.factories import SupplierFactory
from supplier.models import Supplier


default_public_profile_data = {
    'name': 'private company',
    'website': 'http://example.com',
    'description': 'Company description',
    'has_exported_before': True,
    'date_of_creation': '2010-10-10',
    'email_address': 'thing@example.com',
    'verified_with_code': True,
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
    company = factories.CompanyFactory(
        name='Test Company', date_of_creation=datetime.date(2000, 10, 10)
    )
    authed_supplier.company = company
    authed_supplier.save()

    response = authed_client.get(reverse('company'))

    expected = {
        'date_of_creation': '2000-10-10',
        'email_address': company.email_address,
        'email_full_name': company.email_full_name,
        'employees': company.employees,
        'facebook_url': company.facebook_url,
        'has_valid_address': True,
        'id': str(company.id),
        'is_exporting_goods': False,
        'is_exporting_services': False,
        'is_published_investment_support_directory': False,
        'is_published_find_a_supplier': False,
        'is_published': False,
        'is_verification_letter_sent': False,
        'keywords': company.keywords,
        'linkedin_url': company.linkedin_url,
        'logo': None,
        'modified': '2016-11-23T11:21:10.977518Z',
        'po_box': company.po_box,
        'sectors': company.sectors,
        'slug': 'test-company',
        'summary': company.summary,
        'supplier_case_studies': [],
        'twitter_url': company.twitter_url,
        'verified_with_code': False,
        'verified_with_preverified_enrolment': False,
        'verified_with_companies_house_oauth2': False,
        'is_uk_isd_company': False,
        'is_verified': False,
        'country': company.country,
        'mobile_number': company.mobile_number,
        'address_line_1': company.address_line_1,
        'address_line_2': company.address_line_2,
        'postal_full_name': company.postal_full_name,
        'number': company.number,
        'website': company.website,
        'description': company.description,
        'has_exported_before': company.has_exported_before,
        'locality': company.locality,
        'name': 'Test Company',
        'postal_code': company.postal_code,
        'export_destinations': [],
        'expertise_industries': [],
        'expertise_regions': [],
        'expertise_products_services': {},
        'expertise_countries': [],
        'expertise_languages': [],
        'export_destinations_other': '',
        'company_type': models.Company.COMPANIES_HOUSE,
        'is_publishable': company.is_publishable,
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

    response = authed_client.put(
        reverse('company'), VALID_REQUEST_DATA, format='json'
    )

    expected = {
        'email_address': company.email_address,
        'email_full_name': company.email_full_name,
        'employees': company.employees,
        'facebook_url': company.facebook_url,
        'has_valid_address': True,
        'id': str(company.id),
        'is_exporting_goods': False,
        'is_exporting_services': False,
        'is_published_investment_support_directory': False,
        'is_published_find_a_supplier': False,
        'is_published': False,
        'is_verification_letter_sent': False,
        'keywords': company.keywords,
        'linkedin_url': company.linkedin_url,
        'logo': None,
        'modified': '2016-11-23T11:21:10.977518Z',
        'po_box': company.po_box,
        'sectors': company.sectors,
        'slug': 'test-company',
        'summary': company.summary,
        'supplier_case_studies': [],
        'twitter_url': company.twitter_url,
        'verified_with_code': False,
        'verified_with_preverified_enrolment': False,
        'verified_with_companies_house_oauth2': False,
        'is_uk_isd_company': False,
        'is_verified': False,
        'export_destinations': ['DE'],
        'expertise_industries': ['INS'],
        'expertise_regions': ['UKG3'],
        'expertise_products_services': {},
        'expertise_countries': ['GB'],
        'expertise_languages': ['ENG'],
        'export_destinations_other': 'LY',
        'company_type': models.Company.COMPANIES_HOUSE,
        'is_publishable': company.is_publishable,
    }
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@freeze_time('2016-11-23T11:21:10.977518Z')
@pytest.mark.django_db
def test_company_update_with_patch(authed_client, authed_supplier):
    company = factories.CompanyFactory(
        number='01234567',
    )
    authed_supplier.company = company
    authed_supplier.save()

    response = authed_client.patch(
        reverse('company'), VALID_REQUEST_DATA, format='json'
    )

    expected = {
        'email_address': company.email_address,
        'email_full_name': company.email_full_name,
        'employees': company.employees,
        'facebook_url': company.facebook_url,
        'has_valid_address': True,
        'id': str(company.id),
        'is_exporting_goods': False,
        'is_exporting_services': False,
        'is_published_investment_support_directory': False,
        'is_published_find_a_supplier': False,
        'is_published': False,
        'is_verification_letter_sent': False,
        'keywords': company.keywords,
        'linkedin_url': company.linkedin_url,
        'logo': None,
        'modified': '2016-11-23T11:21:10.977518Z',
        'po_box': company.po_box,
        'sectors': company.sectors,
        'slug': 'test-company',
        'summary': company.summary,
        'supplier_case_studies': [],
        'twitter_url': company.twitter_url,
        'verified_with_code': False,
        'verified_with_preverified_enrolment': False,
        'verified_with_companies_house_oauth2': False,
        'is_uk_isd_company': False,
        'is_verified': False,
        'export_destinations': ['DE'],
        'expertise_industries': ['INS'],
        'expertise_regions': ['UKG3'],
        'expertise_products_services': {},
        'expertise_countries': ['GB'],
        'expertise_languages': ['ENG'],
        'export_destinations_other': 'LY',
        'company_type': models.Company.COMPANIES_HOUSE,
        'is_publishable': company.is_publishable,
    }
    expected.update(VALID_REQUEST_DATA)
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@freeze_time('2016-11-23T11:21:10.977518Z')
@pytest.mark.django_db
def test_company_not_update_modified(authed_client, authed_supplier):
    company = factories.CompanyFactory(
        number='01234567',
        has_exported_before=True,
    )
    authed_supplier.company = company
    authed_supplier.save()

    data = {
        **VALID_REQUEST_DATA,
        'modified': '2013-03-09T23:28:53.977518Z'
    }
    for method in [authed_client.put, authed_client.patch]:
        response = method(reverse('company'), data, format='json')
        assert response.status_code == status.HTTP_200_OK
        # modified was not effected by the data we tried to pass
        assert response.json()['modified'] == '2016-11-23T11:21:10.977518Z'


@pytest.mark.django_db
@patch('company.views.CompanyNumberValidatorAPIView.get_serializer')
def test_company_number_validator_rejects_invalid_data(
    mock_get_serializer, client
):
    serializer = MockInvalidSerializer(data={})
    mock_get_serializer.return_value = serializer
    response = client.get(reverse('validate-company-number'), {})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == serializer.errors


@pytest.mark.django_db
@patch('company.views.CompanyNumberValidatorAPIView.get_serializer')
def test_company_number_validator_accepts_valid_data(
    mock_get_serializer, client
):
    mock_get_serializer.return_value = MockValidSerializer(data={})
    response = client.get(reverse('validate-company-number'), {})
    assert response.status_code == status.HTTP_200_OK


def mock_save(self, name, content, max_length=None):
    return Mock(url=content.name)


def get_test_image(extension="PNG"):
    image = Image.new("RGB", (300, 50))
    draw = ImageDraw.Draw(image)
    draw.text((0, 0), "This text is drawn on image")
    byte_io = BytesIO()
    image.save(byte_io, extension)
    byte_io.seek(0)
    return byte_io


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
        verified_with_code=True,
        email_address='test@example.com',
        **VALID_REQUEST_DATA
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
    company = factories.CompanyFactory(
        is_published_find_a_supplier=True
    )
    factories.CompanyCaseStudyFactory(company=company)
    return company


@pytest.fixture
def public_profile_with_case_studies():
    company = factories.CompanyFactory(
        is_published_find_a_supplier=True
    )
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
def supplier_case_study(case_study_data, company):
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
    return Supplier.objects.create(
        sso_id=2,
        company_email='someone@example.com',
        company=company,
    )


@pytest.fixture
def search_case_studies_data(settings):
    AEROSPACE = sectors.AEROSPACE
    AIRPORTS = sectors.AIRPORTS
    company = factories.CompanyFactory(
        is_published_find_a_supplier=True
    )
    factories.CompanyCaseStudyFactory(pk=1, company=company, sector=AEROSPACE)
    factories.CompanyCaseStudyFactory(pk=2, company=company, sector=AEROSPACE)
    factories.CompanyCaseStudyFactory(pk=7, company=company, sector=AIRPORTS)
    factories.CompanyCaseStudyFactory(pk=8, company=company, sector=AIRPORTS)
    Index(settings.ELASTICSEARCH_CASE_STUDY_INDEX_ALIAS).refresh()


@pytest.fixture
def search_companies_data(settings):
    wolf_company = factories.CompanyFactory(
        name='Wolf limited',
        description='Providing the stealth and prowess of wolves.',
        summary='Hunts in packs',
        is_published_find_a_supplier=True,
        keywords='Packs, Hunting, Stark, Teeth',
        sectors=[sectors.AEROSPACE, sectors.AIRPORTS],
        id=1,
    )
    aardvark_company = factories.CompanyFactory(
        name='Aardvark limited',
        description='Providing the power and beauty of Aardvarks.',
        summary='Like an Aardvark',
        is_published_find_a_supplier=True,
        keywords='Ants, Tongue, Anteater',
        sectors=[sectors.AEROSPACE],
        id=2,
    )
    factories.CompanyFactory(
        name='Grapeshot limited',
        description='Providing the destructiveness of grapeshot.',
        summary='Like naval warfare',
        is_published_find_a_supplier=True,
        keywords='Pirates, Ocean, Ship',
        sectors=[sectors.AIRPORTS, sectors.FOOD_AND_DRINK],
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
    Index(settings.ELASTICSEARCH_CASE_STUDY_INDEX_ALIAS).refresh()


@pytest.fixture
def search_companies_highlighting_data(settings):
    factories.CompanyFactory(
        name='Wolf limited',
        description=(
            'Providing the stealth and prowess of wolves. This is a very long '
            'thing about wolf stuff. Lets see what happens in the test when '
            'ES encounters a long  description. Perhaps it will concatenate. '
        ) + ('It is known. ' * 30) + (
            'The wolf cries at night.'
        ),
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
    Index(settings.ELASTICSEARCH_CASE_STUDY_INDEX_ALIAS).refresh()


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
    factories.CompanyCaseStudyFactory(
        company=wolf_three,
        title='cannons better than grapeshot',
        description='guns'
    )
    factories.CompanyCaseStudyFactory(company=wolf_three)
    factories.CompanyCaseStudyFactory(
        company=grapeshot_company,
        title='cannons',
        description='guns'
    )
    factories.CompanyCaseStudyFactory(
        company=grapeshot_company,
        title='cannons',
        description='naval guns'
    )
    Index(settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS).refresh()


@pytest.fixture
def companies_house_oauth_invalid_access_token(requests_mocker):
    return requests_mocker.get(
        'https://account.companieshouse.gov.uk/oauth2/verify',
        status_code=400
    )


@pytest.fixture
def companies_house_oauth_wrong_company(requests_mocker, authed_supplier):
    scope = helpers.CompaniesHouseClient.endpoints['profile'].format(
        number='{number}rad'.format(number=authed_supplier.company.number)
    )
    return requests_mocker.get(
        'https://account.companieshouse.gov.uk/oauth2/verify',
        status_code=200,
        json={
            'scope': scope,
            'expires_in': 6000,
        }
    )


@pytest.fixture
def companies_house_oauth_expired_token(requests_mocker, authed_supplier):
    scope = helpers.CompaniesHouseClient.endpoints['profile'].format(
        number=authed_supplier.company.number
    )
    return requests_mocker.get(
        'https://account.companieshouse.gov.uk/oauth2/verify',
        status_code=200,
        json={
            'scope': scope,
            'expires_in': -1,
        }
    )


@pytest.fixture
def companies_house_oauth_valid_token(requests_mocker, authed_supplier):
    scope = helpers.CompaniesHouseClient.endpoints['profile'].format(
        number=authed_supplier.company.number
    )
    return requests_mocker.get(
        'https://account.companieshouse.gov.uk/oauth2/verify',
        status_code=200,
        json={
            'scope': scope,
            'expires_in': 6000,
        }
    )


@pytest.mark.django_db
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_update(
    company_data, authed_client, authed_supplier, company
):
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
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_create(
    case_study_data, authed_client, authed_supplier, company,
    mock_elasticsearch_company_save
):
    authed_supplier.company = company
    authed_supplier.save()

    response = authed_client.post(
        reverse('company-case-study'), case_study_data, format='multipart'
    )
    assert response.status_code == http.client.CREATED

    instance = models.CompanyCaseStudy.objects.get(pk=response.data['pk'])
    assert instance.testimonial == case_study_data['testimonial']
    assert instance.testimonial_name == case_study_data['testimonial_name']
    assert instance.testimonial_job_title == (
        case_study_data['testimonial_job_title']
    )
    assert instance.testimonial_company == (
        case_study_data['testimonial_company']
    )
    assert instance.website == case_study_data['website']
    assert instance.company == company
    assert instance.description == case_study_data['description']
    assert instance.title == case_study_data['title']
    assert instance.sector == case_study_data['sector']
    assert instance.keywords == case_study_data['keywords']


@pytest.mark.django_db
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_create_invalid_image(
    authed_client, authed_supplier, company
):
    authed_supplier.company = company
    authed_supplier.save()

    case_study_data = {
        'company': company.pk,
        'title': 'a title',
        'description': 'a description',
        'sector': choices.INDUSTRIES[1][0],
        'website': 'http://www.example.com',
        'keywords': 'good, great',
        'image_one': get_test_image(extension="BMP"),
        'image_two': get_test_image(extension="TIFF"),
        'image_three': get_test_image(extension="GIF"),
        'testimonial': 'very nice',
        'testimonial_name': 'Lord Voldemort',
        'testimonial_job_title': 'Evil overlord',
        'testimonial_company': 'Death Eaters',
    }
    response = authed_client.post(
        reverse('company-case-study'), case_study_data, format='multipart'
    )

    assert response.status_code == http.client.BAD_REQUEST


@pytest.mark.django_db
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_create_not_an_image(
    video, authed_client, authed_supplier, company,
):
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
    response = authed_client.post(
        reverse('company-case-study'), case_study_data, format='multipart'
    )

    assert response.status_code == http.client.BAD_REQUEST


@pytest.mark.django_db
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_create_company_not_published(
    video, authed_client, authed_supplier
):

    company = factories.CompanyFactory.create(
        number='01234567',
        has_exported_before=True,
        is_published_find_a_supplier=False
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
        'image_one': get_test_image(extension="PNG"),
        'testimonial': 'very nice',
        'testimonial_name': 'Lord Voldemort',
        'testimonial_job_title': 'Evil overlord',
        'testimonial_company': 'Death Eaters',
    }
    response = authed_client.post(
        reverse('company-case-study'), case_study_data, format='multipart'
    )

    assert response.status_code == http.client.CREATED

    url = reverse(
        'public-case-study-detail', kwargs={'pk': response.data['pk']}
    )
    response = authed_client.get(url)

    assert response.status_code == http.client.NOT_FOUND


@pytest.mark.django_db
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_update(
    supplier_case_study, authed_supplier, authed_client,
    mock_elasticsearch_company_save
):
    authed_supplier.company = supplier_case_study.company
    authed_supplier.save()

    url = reverse(
        'company-case-study-detail', kwargs={'pk': supplier_case_study.pk}
    )
    data = {'title': '2015'}

    assert supplier_case_study.title != data['title']

    response = authed_client.patch(url, data, format='multipart')
    supplier_case_study.refresh_from_db()

    assert response.status_code == http.client.OK
    assert supplier_case_study.title == data['title']


@pytest.mark.django_db
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_delete(
    supplier_case_study, authed_supplier, authed_client
):
    authed_supplier.company = supplier_case_study.company
    authed_supplier.save()

    pk = supplier_case_study.pk
    url = reverse(
        'company-case-study-detail', kwargs={'pk': pk}
    )

    response = authed_client.delete(url)

    assert response.status_code == http.client.NO_CONTENT
    assert models.CompanyCaseStudy.objects.filter(pk=pk).exists() is False


@pytest.mark.django_db
def test_company_case_study_get(
    supplier_case_study, authed_supplier, authed_client
):
    authed_supplier.company = supplier_case_study.company
    authed_supplier.save()

    url = reverse(
        'company-case-study-detail', kwargs={'pk': supplier_case_study.pk}
    )

    response = authed_client.get(url)
    data = response.json()

    assert response.status_code == http.client.OK
    assert data['testimonial'] == supplier_case_study.testimonial
    assert data['testimonial_name'] == supplier_case_study.testimonial_name
    assert data['testimonial_job_title'] == (
        supplier_case_study.testimonial_job_title
    )
    assert data['testimonial_company'] == (
        supplier_case_study.testimonial_company
    )
    assert data['website'] == supplier_case_study.website
    assert data['description'] == supplier_case_study.description
    assert data['title'] == supplier_case_study.title
    assert data['sector'] == supplier_case_study.sector
    assert data['keywords'] == supplier_case_study.keywords
    assert isinstance(data['company'], dict)
    assert data['company']['id'] == supplier_case_study.company.pk


@pytest.mark.django_db
def test_public_company_case_study_get(
    supplier_case_study, supplier, api_client
):
    pk = supplier_case_study.pk
    url = reverse(
        'public-case-study-detail', kwargs={'pk': pk}
    )

    response = api_client.get(url)
    data = response.json()

    assert response.status_code == http.client.OK
    assert data['testimonial'] == supplier_case_study.testimonial
    assert data['testimonial_name'] == supplier_case_study.testimonial_name
    assert data['testimonial_job_title'] == (
        supplier_case_study.testimonial_job_title
    )
    assert data['testimonial_company'] == (
        supplier_case_study.testimonial_company
    )
    assert data['website'] == supplier_case_study.website
    assert data['description'] == supplier_case_study.description
    assert data['title'] == supplier_case_study.title
    assert data['sector'] == supplier_case_study.sector
    assert data['keywords'] == supplier_case_study.keywords
    assert isinstance(data['company'], dict)
    assert data['company']['id'] == supplier_case_study.company.pk


@pytest.mark.django_db
def test_company_profile_public_retrieve_public_profile(
    public_profile, api_client
):
    url = reverse(
        'company-public-profile-detail',
        kwargs={'companies_house_number': public_profile.number}
    )
    response = api_client.get(url)

    assert response.status_code == http.client.OK
    assert response.json()['id'] == str(public_profile.pk)


@pytest.mark.django_db
def test_company_profile_public_404_private_profile(
    private_profile, api_client
):
    url = reverse(
        'company-public-profile-detail',
        kwargs={'companies_house_number': private_profile.number}
    )
    response = api_client.get(url)

    assert response.status_code == http.client.NOT_FOUND


@pytest.mark.django_db
def test_company_profile_public_list_profiles(
    private_profile, public_profile, api_client
):
    url = reverse('company-public-profile-list',)
    response = api_client.get(url)

    assert response.status_code == http.client.OK
    data = response.json()

    assert data['count'] == 1
    assert data['results'][0]['id'] == str(public_profile.pk)


@pytest.mark.django_db
def test_company_profile_public_list_profiles_ordering(
    private_profile, public_profile, public_profile_software,
    public_profile_with_case_study, public_profile_with_case_studies,
    public_profile_cars, api_client
):
    url = reverse('company-public-profile-list')
    response = api_client.get(url)

    data = response.json()
    assert response.status_code == http.client.OK

    expected_sorted_ids = [
        public_profile_with_case_studies.id,
        public_profile_with_case_study.id,
        public_profile_cars.id,
        public_profile_software.id,
        public_profile.id,
    ]
    actual_sorted_ids = [int(company['id']) for company in data['results']]
    assert actual_sorted_ids == expected_sorted_ids


@pytest.mark.django_db
def test_company_profile_public_list_profiles_filter_single(
    public_profile_software, public_profile_cars, public_profile_smart_cars,
    api_client
):
    url = reverse('company-public-profile-list')

    filter_one = {'sectors': 'SOFTWARE_AND_COMPUTER_SERVICES'}
    parsed_one = api_client.get(url, filter_one).json()
    parsed_one_ids = [int(item['id']) for item in parsed_one['results']]
    assert parsed_one['count'] == 2
    assert public_profile_software.pk in parsed_one_ids
    assert public_profile_smart_cars.pk in parsed_one_ids
    assert public_profile_cars.pk not in parsed_one_ids

    filter_two = {'sectors': 'AUTOMOTIVE'}
    parsed_two = api_client.get(url, filter_two).json()
    parsed_two_ids = [int(item['id']) for item in parsed_two['results']]
    assert parsed_two['count'] == 2
    assert public_profile_cars.pk in parsed_two_ids
    assert public_profile_smart_cars.pk in parsed_two_ids
    assert public_profile_software.pk not in parsed_two_ids


@pytest.mark.django_db
def test_company_profile_public_list_profiles_empty_filter(
    public_profile_software, public_profile_cars, public_profile_smart_cars,
    api_client
):
    url = reverse('company-public-profile-list')

    parsed = api_client.get(url).json()
    parsed_ids = [int(item['id']) for item in parsed['results']]
    assert parsed['count'] == 3
    assert public_profile_software.pk in parsed_ids
    assert public_profile_smart_cars.pk in parsed_ids
    assert public_profile_cars.pk in parsed_ids


@pytest.mark.django_db
def test_verify_company_with_code(authed_client, authed_supplier, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with patch('requests.post'):
        company = models.Company.objects.create(**{
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
        })

    authed_supplier.company = company
    authed_supplier.save()

    company.refresh_from_db()
    assert company.verification_code

    url = reverse('company-verify')
    response = authed_client.post(
        url, {'code': company.verification_code}, format='json'
    )

    assert response.status_code == http.client.OK

    company.refresh_from_db()
    assert company.verified_with_code is True


@pytest.mark.django_db
def test_verify_company_with_code_invalid_code(
    authed_client, authed_supplier, settings
):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with patch('requests.post'):
        company = models.Company.objects.create(**{
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
        })

    authed_supplier.company = company
    authed_supplier.save()

    company.refresh_from_db()
    assert company.verification_code
    response = authed_client.post(
         reverse('company-verify'), {'code': 'invalid'}, format='json'
    )

    assert response.status_code == http.client.BAD_REQUEST

    company.refresh_from_db()
    assert company.verified_with_code is False


@patch('company.views.CompanySearchAPIView.get_search_results')
def test_company_search(mock_get_search_results, api_client):
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
        'sectors': [sectors.AEROSPACE],
    }
    response = api_client.get(reverse('company-search'), data=data)

    assert response.status_code == 200
    assert response.json() == expected_value
    assert mock_get_search_results.call_args == call(
        term='bones',
        page=1,
        size=10,
        sectors={sectors.AEROSPACE},
        is_showcase_company=None,
    )


@patch('company.views.CompanySearchAPIView.get_search_results')
def test_company_search_no_sectors(mock_get_search_results, api_client):
    mock_get_search_results.return_value = expected_value = {
        'hits': {
            'total': 2,
            'hits': [None, None],
        },
    }
    data = {'term': 'bones', 'page': 1, 'size': 10}
    response = api_client.get(reverse('company-search'), data=data)

    assert response.status_code == 200
    assert response.json() == expected_value
    assert mock_get_search_results.call_count == 1
    assert mock_get_search_results.call_args == call(
        term='bones',
        page=1,
        size=10,
        sectors=set(),
        is_showcase_company=None,
    )


@patch('company.views.CompanySearchAPIView.get_search_results')
def test_company_search_showcase(mock_get_search_results, api_client):
    mock_get_search_results.return_value = expected_value = {
        'hits': {
            'total': 2,
            'hits': [None, None],
        },
    }
    data = {'term': 'abc', 'page': 1, 'size': 10, 'is_showcase_company': True}
    response = api_client.get(reverse('company-search'), data=data)

    assert response.status_code == 200
    assert response.json() == expected_value
    assert mock_get_search_results.call_count == 1
    assert mock_get_search_results.call_args == call(
        term='abc',
        page=1,
        size=10,
        sectors=set(),
        is_showcase_company=True,
    )


@pytest.mark.parametrize('page_number,expected_start', [
    [1, 0],
    [2, 5],
    [3, 10],
    [4, 15],
    [5, 20],
    [6, 25],
    [7, 30],
    [8, 35],
    [9, 40],
])
def test_company_paginate_first_page(
    page_number, expected_start, api_client, settings
):
    es = connections.get_connection('default')
    with patch.object(es, 'search', return_value={}) as mock_search:
        data = {'term': 'bones', 'page': page_number, 'size': 5}
        response = api_client.get(reverse('company-search'), data=data)

        assert response.status_code == 200, response.content
        assert mock_search.call_count == 1
        assert mock_search.call_args == call(
            body={
                'highlight': {
                    'fields': {
                        'summary': {},
                        'description': {}
                    },
                    'require_field_match': False
                },
                'query': {
                    'function_score': {
                        'query': {
                            'bool': {
                                'minimum_should_match': 0,
                                'must': [
                                    {
                                        'match_phrase': {
                                            '_all': 'bones'
                                        }
                                    }
                                ]
                            }
                        },
                        'boost_mode': 'sum',
                        'functions': [
                            {
                                'weight': 5,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'range': {
                                                    'case_study_count': {
                                                        'gt': 1
                                                    }
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': True
                                                }
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                'weight': 4,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'range': {
                                                    'case_study_count': {
                                                        'gt': 1
                                                    }
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': False
                                                }
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                'weight': 3,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'term': {
                                                    'case_study_count': 1
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': True
                                                }
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                'weight': 2,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'term': {
                                                    'case_study_count': 1
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': False
                                                }
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                'weight': 1,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'term': {
                                                    'case_study_count': 0
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': True
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ]
                    }
                },
                'from': expected_start,
                'size': 5
            },
            doc_type=['company_doc_type'],
            index=[settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS]
        )


def test_company_search_with_sector_filter(api_client, settings):
    es = connections.get_connection('default')
    with patch.object(es, 'search', return_value={}) as mock_search:
        data = {
            'term': 'bees',
            'sectors': [sectors.AEROSPACE],
            'size': 5,
            'page': 1,
        }
        response = api_client.get(reverse('company-search'), data=data)

        assert response.status_code == 200, response.content
        assert mock_search.call_args == call(
            body={
                'highlight': {
                    'fields': {
                        'summary': {},
                        'description': {}
                    },
                    'require_field_match': False
                },
                'size': 5,
                'query': {
                    'function_score': {
                        'boost_mode': 'sum',
                        'functions': [
                            {
                                'weight': 5,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'range': {
                                                    'case_study_count': {
                                                        'gt': 1
                                                    }
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': True
                                                }
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                'weight': 4,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'range': {
                                                    'case_study_count': {
                                                        'gt': 1
                                                    }
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': False
                                                }
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                'weight': 3,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'term': {
                                                    'case_study_count': 1
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': True
                                                }
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                'weight': 2,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'term': {
                                                    'case_study_count': 1
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': False
                                                }
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                'weight': 1,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'term': {
                                                    'case_study_count': 0
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': True
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ],
                        'query': {
                            'bool': {
                                'minimum_should_match': 1,
                                'must': [{
                                    'match_phrase': {
                                        '_all': 'bees'
                                    }
                                }],
                                'should': [{
                                    'match': {
                                        'sectors': sectors.AEROSPACE
                                    }
                                }]
                            }
                        }
                    }
                },
                'from': 0
            },
            doc_type=['company_doc_type'],
            index=[settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS]
        )


def test_company_search_with_sector_filter_only(api_client, settings):
    es = connections.get_connection('default')
    with patch.object(es, 'search', return_value={}) as mock_search:
        data = {'sectors': [sectors.AEROSPACE], 'size': 5, 'page': 1}
        response = api_client.get(reverse('company-search'), data=data)

        assert response.status_code == 200, response.content
        assert mock_search.call_args == call(
            body={
                'highlight': {
                    'fields': {
                        'summary': {},
                        'description': {}
                    },
                    'require_field_match': False
                },
                'query': {
                    'function_score': {
                        'boost_mode': 'sum',
                        'functions': [
                            {
                                'weight': 5,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'range': {
                                                    'case_study_count': {
                                                        'gt': 1
                                                    }
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': True
                                                }
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                'weight': 4,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'range': {
                                                    'case_study_count': {
                                                        'gt': 1
                                                    }
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': False
                                                }
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                'weight': 3,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'term': {
                                                    'case_study_count': 1
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': True
                                                }
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                'weight': 2,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'term': {
                                                    'case_study_count': 1
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': False
                                                }
                                            }
                                        ]
                                    }
                                }
                            },
                            {
                                'weight': 1,
                                'filter': {
                                    'bool': {
                                        'must': [
                                            {
                                                'term': {
                                                    'case_study_count': 0
                                                }
                                            },
                                            {
                                                'term': {
                                                    'has_description': True
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        ],
                        'query': {
                            'bool': {
                                'minimum_should_match': 1,
                                'should': [{
                                    'match': {
                                        'sectors': sectors.AEROSPACE
                                    }
                                }]
                            }
                        },
                    }
                },
                'from': 0,
                'size': 5
            },
            doc_type=['company_doc_type'],
            index=[settings.ELASTICSEARCH_COMPANY_INDEX_ALIAS]
        )


@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
@pytest.mark.parametrize('term,sector,expected', [
    # sectors
    ['',           [sectors.AEROSPACE],                   ['1', '2']],
    ['',           [sectors.AEROSPACE, sectors.AIRPORTS], ['1', '2', '3']],
    # company name
    ['wolf',       None,                                  ['1']],
    ['Aardvark',   None,                                  ['2']],
    ['grapeshot',  None,                                  ['3']],
    ['wolf',       [sectors.AEROSPACE, sectors.AIRPORTS], ['1']],
    ['wolf',       [sectors.AEROSPACE],                   ['1']],
    ['wolf',       [sectors.AIRPORTS],                    ['1']],
    ['Aardvark',   [sectors.AEROSPACE, sectors.AIRPORTS], ['2']],
    # company description
    ['stealth',    None,                                  ['1']],
    ['beauty',     None,                                  ['2']],
    ['Providing',  None,                                  ['1', '2', '3']],
    ['stealth',    [sectors.AEROSPACE],                   ['1']],
    ['stealth',    [sectors.FOOD_AND_DRINK],              []],
    ['beauty',     [sectors.AEROSPACE],                   ['2']],
    ['beauty',     [sectors.FOOD_AND_DRINK],              []],
    ['Providing',  [sectors.AEROSPACE],                   ['1', '2']],
    ['Providing',  ['TECHNOLOGY'],                        []],
    # company keywords
    ['Hunting',    None,                                  ['1']],
    ['Hunting',    [sectors.AEROSPACE, sectors.AIRPORTS], ['1']],
    ['Hunting',    [sectors.FOOD_AND_DRINK],              []],
    # case study description
    ['lead',       None,                                  ['2']],
    ['lead',       [sectors.AEROSPACE],                   ['2']],
    ['lead',       [sectors.AEROSPACE, sectors.AIRPORTS], ['2']],
    ['lead',       [sectors.FOOD_AND_DRINK],              []],
    # case study title
    ['case study', None,                                  ['1', '2']],
    ['case study', [sectors.FOOD_AND_DRINK],              []],
    ['case study', [sectors.AIRPORTS],                    ['1']],

])
def test_company_search_results(term, sector, expected, search_companies_data):
    results = views.CompanySearchAPIView().get_search_results(
        term=term, page=1, size=5, sectors=sector,
    )
    hits = results['hits']['hits']

    assert len(hits) == len(expected)
    for hit in hits:
        assert hit['_id'] in expected


@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
@pytest.mark.parametrize('sector,expected', [
    [sectors.AEROSPACE, ['1', '2']],
    [sectors.AIRPORTS,  ['8', '7']],
])
def test_case_study_search_results(sector, expected, search_case_studies_data):
    results = views.CaseStudySearchAPIView().get_search_results(
        term='', page=1, size=5, sectors=[sector]
    )
    hits = results['hits']['hits']
    assert len(hits) == len(expected)
    for hit in hits:
        assert hit['_id'] in expected


@pytest.mark.django_db
@pytest.mark.rebuild_elasticsearch
@pytest.mark.parametrize('term,sectors,expected', [
    ['wolf',       None,                ['3', '4', '2', '1']],
    ['Limited',    None,                ['3', '5', '4', '2', '1']],
    ['packs',      None,                ['3', '2', '1']],
    ['',           [sectors.AEROSPACE], ['4', '3', '1']],
    ['Grapeshot',  None,                ['2', '5']],
    ['cannons',    None,                ['5', '2']],
    ['guns',       None,                ['5', '2']],
])
def test_company_search_results_ordering(
    term, expected, sectors, search_companies_ordering_data
):
    results = views.CompanySearchAPIView().get_search_results(
        term=term, page=1, size=5, sectors=sectors
    )
    hits = results['hits']['hits']

    ordered_hit_ids = [hit['_id'] for hit in hits]

    assert ordered_hit_ids == expected


@pytest.mark.django_db
@pytest.mark.rebuild_elasticsearch
def test_company_search_results_highlight(search_companies_highlighting_data):
    results = views.CompanySearchAPIView().get_search_results(
        term='power', page=1, size=5, sectors=None,
    )
    hits = results['hits']['hits']

    assert hits[0]['highlight'] == {
        'description': [
            'Providing the <em>power</em> and beauty of Aardvarks.'
        ]
    }


@pytest.mark.django_db
@pytest.mark.rebuild_elasticsearch
def test_company_search_results_highlight_long(
    search_companies_highlighting_data
):
    results = views.CompanySearchAPIView().get_search_results(
        term='wolf', page=1, size=5, sectors=None,
    )
    hits = results['hits']['hits']

    assert '...'.join(hits[0]['highlight']['description']) == (
        'Providing the stealth and prowess of wolves. This is a very '
        'long thing about <em>wolf</em> stuff. Lets see... known. It is '
        'known. It is known. It is known. It is known. It is known. It is '
        'known. The <em>wolf</em> cries at night.'
    )


@pytest.mark.django_db
def test_verify_companies_house_missing_access_token(
    authed_client, authed_supplier
):
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
    assert response.json() == {
        'access_token': [serializer.MESSAGE_BAD_ACCESS_TOKEN]
    }
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
    assert response.json() == {
        'access_token': [serializer.MESSAGE_SCOPE_ERROR]
    }
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
    assert response.json() == {
        'access_token': [serializer.MESSAGE_EXPIRED]
    }
    company = authed_supplier.company
    company.refresh_from_db()
    assert company.verified_with_companies_house_oauth2 is False


@pytest.mark.django_db
def test_verify_companies_house_good_access_token(
    companies_house_oauth_valid_token, authed_supplier, authed_client,
    mock_elasticsearch_company_save
):
    url = reverse('company-verify-companies-house')
    response = authed_client.post(url, {'access_token': '123'})

    assert response.status_code == 200
    company = authed_supplier.company
    company.refresh_from_db()
    assert company.verified_with_companies_house_oauth2 is True


@pytest.mark.django_db
@patch('core.tasks.send_email', Mock())
def test_create_transfer_ownership_invite(authed_client, authed_supplier):

    data = {'new_owner_email': 'foo@bar.com'}
    url = reverse('transfer-ownership-invite')
    response = authed_client.post(url, data=data)

    assert response.status_code == status.HTTP_201_CREATED
    invite = models.OwnershipInvite.objects.get(
        new_owner_email='foo@bar.com'
    )
    assert response.json() == {
        'uuid': str(invite.uuid),
        'company': authed_supplier.company.pk,
        'company_name': invite.company.name,
        'requestor': authed_supplier.pk,
        'new_owner_email': 'foo@bar.com'
    }
    assert invite.company == authed_supplier.company
    assert invite.requestor == authed_supplier
    assert isinstance(invite.uuid, uuid.UUID)


@pytest.mark.django_db
@patch('core.tasks.send_email', Mock())
def test_create_duplicated_transfer_ownership_invite(
        authed_client,
        authed_supplier):

    invite = models.OwnershipInvite(
        new_owner_email='foo@bar.com',
        company=authed_supplier.company,
        requestor=authed_supplier,
    )
    invite.save()

    data = {
        'new_owner_email': 'foo@bar.com',
        'company': authed_supplier.company.pk,
    }
    response = authed_client.post(
        reverse('transfer-ownership-invite'),
        data=data,
        format='json'
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'new_owner_email': [
            'ownership invite with this new owner email already exists.'
        ]
    }


@pytest.mark.django_db
def test_remove_collaborators(authed_client, authed_supplier):
    authed_supplier.is_company_owner = True
    authed_supplier.save()

    supplier_one = SupplierFactory(
        company=authed_supplier.company, is_company_owner=False
    )
    supplier_two = SupplierFactory(
        company=authed_supplier.company, is_company_owner=False
    )
    supplier_three = SupplierFactory(
        company=authed_supplier.company, is_company_owner=False
    )
    supplier_four = SupplierFactory(
        is_company_owner=False
    )

    suppliers_before = authed_supplier.company.suppliers.all()
    assert supplier_one in suppliers_before
    assert supplier_two in suppliers_before
    assert supplier_three in suppliers_before
    assert supplier_four not in suppliers_before
    assert authed_supplier in suppliers_before

    url = reverse('remove-collaborators')
    data = {'sso_ids': [supplier_one.sso_id, supplier_two.sso_id]}
    response = authed_client.post(url, data=data)

    assert response.status_code == 200
    suppliers_after = authed_supplier.company.suppliers.all()
    assert supplier_one not in suppliers_after
    assert supplier_two not in suppliers_after
    assert supplier_three in suppliers_after
    assert supplier_four not in suppliers_after
    assert authed_supplier in suppliers_after


@pytest.mark.django_db
def test_remove_collaborators_cannot_remove_self(
    authed_client, authed_supplier
):
    authed_supplier.is_company_owner = True
    authed_supplier.save()

    assert authed_supplier in authed_supplier.company.suppliers.all()

    url = reverse('remove-collaborators')
    data = {'sso_ids': [authed_supplier.sso_id]}
    response = authed_client.post(url, data=data)

    assert response.status_code == 200
    assert authed_supplier in authed_supplier.company.suppliers.all()


@pytest.mark.django_db
@patch('core.tasks.send_email', Mock())
def test_retrieve_transfer_ownership_invite(
        authed_client,
        authed_supplier):

    invite = models.OwnershipInvite(
        new_owner_email='foo@bar.com',
        company=authed_supplier.company,
        requestor=authed_supplier,
    )
    invite.save()

    response = authed_client.get(
        reverse('transfer-ownership-invite-detail',
                kwargs={'uuid': str(invite.uuid)})
    )

    assert response.status_code == status.HTTP_200_OK
    expected_response = {
        'uuid': str(invite.uuid),
        'company_name': invite.company.name,
        'company': invite.company.pk,
        'new_owner_email': invite.new_owner_email,
        'requestor': invite.requestor.pk
    }
    assert response.json() == expected_response


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
@patch('core.tasks.send_email', Mock())
def test_accept_transfer_ownership_invite(
        authed_client,
        authed_supplier):

    authed_supplier.delete()

    supplier = SupplierFactory(is_company_owner=False)

    invite = models.OwnershipInvite(
        new_owner_email=authed_supplier.company_email,
        company=supplier.company,
        requestor=supplier,
    )
    invite.save()
    response = authed_client.patch(
        reverse('transfer-ownership-invite-detail',
                kwargs={'uuid': str(invite.uuid)}),
        {'accepted': True}
    )

    assert response.status_code == 200

    invite.refresh_from_db()
    expected_date = '2016-11-23T11:21:10.977518+00:00'
    assert invite.accepted is True
    assert invite.accepted_date.isoformat() == expected_date
    assert supplier.is_company_owner is False
    assert Supplier.objects.filter(
        company=supplier.company,
        is_company_owner=True,
        company_email=invite.new_owner_email
    ).count() == 1


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
@patch('core.tasks.send_email', Mock())
def test_accept_transfer_ownership_invite_case_insensitive(
        authed_client,
        authed_supplier):

    authed_supplier.delete()

    supplier = SupplierFactory(is_company_owner=False)

    invite = models.OwnershipInvite(
        new_owner_email=authed_supplier.company_email.upper(),
        company=supplier.company,
        requestor=supplier,
    )
    invite.save()
    response = authed_client.patch(
        reverse('transfer-ownership-invite-detail',
                kwargs={'uuid': str(invite.uuid)}),
        {'accepted': True}
    )

    assert response.status_code == 200

    invite.refresh_from_db()
    expected_date = '2016-11-23T11:21:10.977518+00:00'
    assert invite.accepted is True
    assert invite.accepted_date.isoformat() == expected_date
    assert supplier.is_company_owner is False
    assert Supplier.objects.filter(
        company=supplier.company,
        company_email=invite.new_owner_email,
        is_company_owner=True
    ).count() == 1


@pytest.mark.django_db
@patch('core.tasks.send_email', Mock())
def test_accept_wrong_transfer_ownership_invite(
        authed_client,
        authed_supplier):

    authed_supplier.delete()

    supplier = SupplierFactory(is_company_owner=True)

    invite = models.OwnershipInvite(
        new_owner_email='foo@bar.com',
        company=supplier.company,
        requestor=supplier,
    )
    invite.save()
    response = authed_client.patch(
        reverse('transfer-ownership-invite-detail',
                kwargs={'uuid': str(invite.uuid)}),
        {'accepted': True}
    )
    error = serializers.InviteSerializerMixin.MESSAGE_WRONG_INVITE

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    expected_response = {
        'new_owner_email': [error]
    }
    assert response.json() == expected_response
    assert invite.accepted is False
    assert invite.accepted_date is None
    assert Supplier.objects.filter(
        company=supplier.company,
        is_company_owner=True
    ).count() == 1


@pytest.mark.django_db
@patch('core.tasks.send_email', Mock())
def test_accept_transfer_ownership_invite_to_collaborator(
    authed_client, authed_supplier
):
    authed_supplier.company = None
    authed_supplier.save()

    company = factories.CompanyFactory()
    existing_owner = SupplierFactory(
        company=company,
        is_company_owner=True,
        company_email='owner@example.com',
    )
    invite = models.OwnershipInvite.objects.create(
        new_owner_email=authed_supplier.company_email,
        company=company,
        requestor=existing_owner,
    )
    response = authed_client.patch(
        reverse('transfer-ownership-invite-detail',
                kwargs={'uuid': str(invite.uuid)}),
        {'accepted': True}
    )

    invite.refresh_from_db()

    assert response.status_code == status.HTTP_200_OK
    assert invite.accepted is True


@pytest.mark.django_db
@patch('core.tasks.send_email', Mock())
def test_accept_transfer_ownership_invite_supplier_has_other_company(
    authed_client, authed_supplier
):
    invite = models.OwnershipInvite(
        new_owner_email=authed_supplier.company_email,
        company=factories.CompanyFactory(),
        requestor=authed_supplier,
    )
    invite.save()
    response = authed_client.patch(
        reverse('transfer-ownership-invite-detail',
                kwargs={'uuid': str(invite.uuid)}),
        {'accepted': True}
    )
    error = serializers.InviteSerializerMixin.MESSAGE_ALREADY_HAS_COMPANY

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    expected_response = {
        'new_owner_email': [error]
    }
    assert response.json() == expected_response
    assert invite.accepted is False
    assert invite.accepted_date is None


@pytest.mark.django_db
@patch('core.tasks.send_email', Mock())
def test_accept_transfer_ownership_invite_requestor_not_legit(
        authed_client,
        authed_supplier):

    authed_supplier.delete()

    supplier = SupplierFactory()
    company = factories.CompanyFactory()

    invite = models.OwnershipInvite(
        new_owner_email=authed_supplier.company_email,
        company=company,
        requestor=supplier,
    )
    invite.save()
    response = authed_client.patch(
        reverse('transfer-ownership-invite-detail',
                kwargs={'uuid': str(invite.uuid)}),
        {'accepted': True}
    )
    invite.refresh_from_db()
    error = serializers.InviteSerializerMixin.MESSAGE_INVALID_REQUESTOR

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    expected_response = {
        'requestor': [error]
    }
    assert response.json() == expected_response
    assert invite.accepted is False
    assert invite.accepted_date is None


@pytest.mark.django_db
@patch('core.tasks.send_email', Mock())
def test_company_create_collaboration_invite(
    authed_client, authed_supplier
):
    data = {'collaborator_email': 'foo@bar.com'}
    url = reverse('collaboration-invite-create')
    response = authed_client.post(url, data=data)

    invite = models.CollaboratorInvite.objects.get(
        collaborator_email='foo@bar.com'
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'uuid': str(invite.uuid),
        'company': authed_supplier.company.pk,
        'company_name': invite.company.name,
        'requestor': authed_supplier.pk,
        'collaborator_email': 'foo@bar.com'
    }

    assert invite.company == authed_supplier.company
    assert invite.requestor == authed_supplier


@pytest.mark.django_db
@patch('core.tasks.send_email', Mock())
def test_company_create_duplicated_collaboration_invite(
    authed_client, authed_supplier
):
    factories.CollaboratorInviteFactory(
        collaborator_email='foo@bar.com',
        company=authed_supplier.company,
        requestor=authed_supplier,
    )

    data = {'collaborator_email': 'foo@bar.com'}
    url = reverse('collaboration-invite-create')
    response = authed_client.post(url, data=data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {
        'collaborator_email': [
            'collaborator invite with this collaborator email already exists.'
        ]
    }


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
@patch('core.tasks.send_email', Mock())
def test_accept_collaborator_invite(
    authed_client, authed_supplier
):
    authed_supplier.delete()

    supplier = SupplierFactory(is_company_owner=False)

    invite = factories.CollaboratorInviteFactory(
        collaborator_email=authed_supplier.company_email,
        company=supplier.company,
        requestor=supplier,
    )

    url = reverse(
        'collaboration-invite-detail', kwargs={'uuid': str(invite.uuid)}
    )
    response = authed_client.patch(url, {'accepted': True})
    assert response.status_code == 200

    invite.refresh_from_db()
    expected_date = '2016-11-23T11:21:10.977518+00:00'
    assert invite.accepted is True
    assert invite.accepted_date.isoformat() == expected_date
    assert supplier.is_company_owner is False
    assert Supplier.objects.filter(
        company=supplier.company,
        is_company_owner=False,
        company_email=invite.collaborator_email
    ).count() == 1


@pytest.mark.django_db
@freeze_time('2016-11-23T11:21:10.977518Z')
@patch('core.tasks.send_email', Mock())
def test_accept_collaborator_invite_case_insensitive(
    authed_client, authed_supplier
):
    authed_supplier.delete()

    supplier = SupplierFactory(is_company_owner=False)

    invite = factories.CollaboratorInviteFactory(
        collaborator_email=authed_supplier.company_email.upper(),
        company=supplier.company,
        requestor=supplier,
    )

    url = reverse(
        'collaboration-invite-detail', kwargs={'uuid': str(invite.uuid)}
    )
    response = authed_client.patch(url, {'accepted': True})
    assert response.status_code == 200

    invite.refresh_from_db()
    expected_date = '2016-11-23T11:21:10.977518+00:00'
    assert invite.accepted is True
    assert invite.accepted_date.isoformat() == expected_date
    assert supplier.is_company_owner is False
    assert Supplier.objects.filter(
        company=supplier.company,
        is_company_owner=False,
        company_email=invite.collaborator_email
    ).count() == 1


@pytest.mark.django_db
@patch('core.tasks.send_email', Mock())
def test_accept_wrong_collaborator_invite(
    authed_client, authed_supplier
):

    authed_supplier.delete()

    supplier = SupplierFactory(is_company_owner=True)

    invite = factories.CollaboratorInviteFactory(
        collaborator_email='foo@bar.com',
        company=supplier.company,
        requestor=supplier,
    )

    url = reverse(
        'collaboration-invite-detail', kwargs={'uuid': str(invite.uuid)}
    )
    response = authed_client.patch(url, {'accepted': True})
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    error = serializers.InviteSerializerMixin.MESSAGE_WRONG_INVITE
    expected_response = {
        'collaborator_email': [error]
    }
    assert response.json() == expected_response
    assert invite.accepted is False
    assert invite.accepted_date is None
    assert Supplier.objects.filter(
        company=supplier.company,
        is_company_owner=True
    ).count() == 1


@pytest.mark.django_db
@patch('core.tasks.send_email', Mock())
def test_accept_collaborator_invite_supplier_has_other_company(
    authed_client, authed_supplier
):

    invite = factories.CollaboratorInviteFactory(
        collaborator_email=authed_supplier.company_email,
        company=factories.CompanyFactory(),
        requestor=authed_supplier,
    )
    url = reverse(
        'collaboration-invite-detail', kwargs={'uuid': str(invite.uuid)}
    )
    response = authed_client.patch(url, {'accepted': True})
    error = serializers.InviteSerializerMixin.MESSAGE_ALREADY_HAS_COMPANY

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    expected_response = {
        'collaborator_email': [error]
    }
    assert response.json() == expected_response
    assert invite.accepted is False
    assert invite.accepted_date is None


@pytest.mark.django_db
@patch('core.tasks.send_email', Mock())
def test_accept_collaborator_invite_requestor_not_legit(
        authed_client,
        authed_supplier):

    authed_supplier.delete()

    supplier = SupplierFactory()
    company = factories.CompanyFactory()

    invite = factories.CollaboratorInviteFactory(
        collaborator_email=authed_supplier.company_email,
        company=company,
        requestor=supplier
    )
    url = reverse(
        'collaboration-invite-detail', kwargs={'uuid': str(invite.uuid)}
    )
    response = authed_client.patch(url, {'accepted': True})
    error = serializers.InviteSerializerMixin.MESSAGE_INVALID_REQUESTOR

    invite.refresh_from_db()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    expected_response = {
        'requestor': [error]
    }
    assert response.json() == expected_response
    assert invite.accepted is False
    assert invite.accepted_date is None


@pytest.mark.django_db
@pytest.mark.parametrize('url', (
    reverse('collaboration-invite-create'),
    reverse('remove-collaborators'),
    reverse('transfer-ownership-invite'),
))
def test_multi_user_account_management_views_forbidden(
    url, authed_client, authed_supplier
):
    authed_supplier.is_company_owner = False
    authed_supplier.save()

    response = authed_client.post(url, {})

    assert response.status_code == 403


@pytest.mark.django_db
def test_collaborator_request(client):
    company = factories.CompanyFactory()

    url = reverse('collaborator-request')
    data = {
        'company_number': company.number,
        'collaborator_email': 'test@example.com',
    }
    response = client.post(url, data, format='json')

    assert response.status_code == 201
    assert response.json() == {'company_email': company.email_address}


@pytest.mark.django_db
def test_collaborator_request_incorrect_number(client):
    url = reverse('collaborator-request')
    data = {
        'company_number': 'asdsadas',
        'collaborator_email': 'test@example.com',
    }
    response = client.post(url, data, format='json')

    assert response.status_code == 400
    assert response.json() == {'__all__': 'Company does not exist'}


@pytest.mark.django_db
def test_collaborator_multiple_times(client):
    company = factories.CompanyFactory()

    url = reverse('collaborator-request')
    data = {
        'company_number': company.number,
        'collaborator_email': 'test@example.com',
    }
    response = client.post(url, data, format='json')

    assert response.status_code == 201

    response = client.post(url, data, format='json')

    assert response.status_code == 400
