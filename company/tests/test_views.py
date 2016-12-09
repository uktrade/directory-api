import datetime
from decimal import Decimal
import http
from io import BytesIO
from unittest.mock import patch, Mock
from unittest import TestCase

from directory_validators.constants import choices
import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient
from rest_framework import status

from django.core.urlresolvers import reverse
from django.test import Client

from company.models import Company, CompanyCaseStudy
from company.tests import (
    MockInvalidSerializer,
    MockValidSerializer,
    VALID_REQUEST_DATA,
)
from user.models import User as Supplier


default_public_profile_data = {
    'name': 'private company',
    'website': 'http://example.com',
    'description': 'Company description',
    'export_status': choices.EXPORT_STATUSES[1][0],
    'date_of_creation': '2010-10-10',
    'revenue': '100000.00',
}


class CompanyViewsTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.signature_permission_mock = patch(
            'signature.permissions.SignaturePermission.has_permission'
        )

        self.signature_permission_mock.start()

    def tearDown(self):
        self.signature_permission_mock.stop()

    @freeze_time('2016-11-23T11:21:10.977518Z')
    @pytest.mark.django_db
    def test_company_retrieve_view(self):
        client = APIClient()
        company = Company.objects.create(**VALID_REQUEST_DATA)
        supplier = Supplier.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com',
            company=company,
        )

        response = client.get(reverse(
            'company', kwargs={'sso_id': supplier.sso_id}
        ))

        expected = {
            'id': str(company.id),
            'logo': None,
            'sectors': None,
            'employees': '',
            'keywords': '',
            'date_of_creation': '10 Oct 2000',
            'supplier_case_studies': [],
            'modified': '2016-11-23T11:21:10.977518Z',
        }
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @pytest.mark.django_db
    def test_company_retrieve_view_404(self):
        client = APIClient()
        company = Company.objects.create(**VALID_REQUEST_DATA)
        Supplier.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com',
            company=company,
        )

        response = client.get(reverse(
            'company', kwargs={'sso_id': 0}
        ))

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @freeze_time('2016-11-23T11:21:10.977518Z')
    @pytest.mark.django_db
    def test_company_update_view_with_put(self):
        client = APIClient()
        company = Company.objects.create(
            number='01234567',
            export_status=choices.EXPORT_STATUSES[1][0],
        )
        supplier = Supplier.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com',
            company=company,
        )

        response = client.put(
            reverse('company', kwargs={'sso_id': supplier.sso_id}),
            VALID_REQUEST_DATA, format='json')

        expected = {
            'id': str(company.id),
            'logo': None,
            'sectors': None,
            'employees': '',
            'keywords': '',
            'date_of_creation': '10 Oct 2000',
            'supplier_case_studies': [],
            'modified': '2016-11-23T11:21:10.977518Z',
        }
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @freeze_time('2016-11-23T11:21:10.977518Z')
    @pytest.mark.django_db
    def test_company_update_view_with_patch(self):
        client = APIClient()
        company = Company.objects.create(
            number='01234567',
            export_status=choices.EXPORT_STATUSES[1][0]

        )
        supplier = Supplier.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com',
            company=company,
        )

        response = client.patch(
            reverse('company', kwargs={'sso_id': supplier.sso_id}),
            VALID_REQUEST_DATA, format='json')

        expected = {
            'id': str(company.id),
            'logo': None,
            'sectors': None,
            'employees': '',
            'keywords': '',
            'date_of_creation': '10 Oct 2000',
            'supplier_case_studies': [],
            'modified': '2016-11-23T11:21:10.977518Z',
        }
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @freeze_time('2016-11-23T11:21:10.977518Z')
    @pytest.mark.django_db
    def test_company_update_view_with_put_ignores_modified(self):
        client = APIClient()
        company = Company.objects.create(
            number='01234567',
            export_status=choices.EXPORT_STATUSES[1][0],
        )
        supplier = Supplier.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com',
            company=company,
        )
        update_data = {'modified': '2013-03-09T23:28:53.977518Z'}
        update_data.update(VALID_REQUEST_DATA)

        response = client.put(
            reverse('company', kwargs={'sso_id': supplier.sso_id}),
            update_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        # modified was not effected by the data we tried to pass
        assert response.json()['modified'] == '2016-11-23T11:21:10.977518Z'

    @freeze_time('2016-11-23T11:21:10.977518Z')
    @pytest.mark.django_db
    def test_company_update_view_with_patch_ignores_modified(self):
        client = APIClient()
        company = Company.objects.create(
            number='01234567',
            export_status=choices.EXPORT_STATUSES[1][0],
        )
        supplier = Supplier.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com',
            company=company,
        )
        update_data = {'modified': '2013-03-09T23:28:53.977518Z'}
        update_data.update(VALID_REQUEST_DATA)

        response = client.patch(
            reverse('company', kwargs={'sso_id': supplier.sso_id}),
            update_data, format='json')

        assert response.status_code == status.HTTP_200_OK
        # modified was not effected by the data we tried to pass
        assert response.json()['modified'] == '2016-11-23T11:21:10.977518Z'

    @pytest.mark.django_db
    @patch('company.views.CompanyNumberValidatorAPIView.get_serializer')
    def test_company_number_validator_rejects_invalid_serializer(
            self, mock_get_serializer):

        serializer = MockInvalidSerializer(data={})
        mock_get_serializer.return_value = serializer
        response = self.client.get(reverse('validate-company-number'), {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.json() == serializer.errors

    @pytest.mark.django_db
    @patch('company.views.CompanyNumberValidatorAPIView.get_serializer')
    def test_company_number_validator_accepts_valid_serializer(
            self, mock_get_serializer):

        mock_get_serializer.return_value = MockValidSerializer(data={})
        response = self.client.get(reverse('validate-company-number'), {})
        assert response.status_code == status.HTTP_200_OK


def mock_save(self, name, content, max_length=None):
    return Mock(url=content.name)


@pytest.fixture(scope='session')
def image_one(tmpdir_factory):
    return BytesIO(b'some text')


@pytest.fixture(scope='session')
def image_two(tmpdir_factory):
    return BytesIO(b'some text')


@pytest.fixture(scope='session')
def image_three(tmpdir_factory):
    return BytesIO(b'some text')


@pytest.fixture(scope='session')
def video(tmpdir_factory):
    return BytesIO(b'some text')


@pytest.fixture
def case_study_data(image_one, image_two, image_three, video, company):
    return {
        'company': company.pk,
        'title': 'a title',
        'description': 'a description',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'year': '2010',
        'keywords': 'good, great',
        'image_one': image_one,
        'image_two': image_two,
        'image_three': image_three,
        'video_one': video,
        'testimonial': 'very nice',
    }


@pytest.fixture
def company_data():
    return {
        'number': '01234567',
        'name': 'Test Company',
        'website': 'http://example.com',
        'description': 'Company description',
        'export_status': choices.EXPORT_STATUSES[1][0],
        'date_of_creation': '2010-10-10',
        'revenue': '100000.00',
    }


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def company():
    return Company.objects.create(**VALID_REQUEST_DATA)


@pytest.fixture
def private_profile():
    company = Company(**default_public_profile_data)
    company.number = '0123456A'
    company.is_published = False
    company.save()
    return company


@pytest.fixture
def public_profile():
    company = Company(**default_public_profile_data)
    company.number = '0123456B'
    company.is_published = True
    company.save()
    return company


@pytest.fixture
def public_profile_software():
    company = Company(**default_public_profile_data)
    company.number = '0123456C'
    company.is_published = True
    company.sectors = ['SOFTWARE_AND_COMPUTER_SERVICES']
    company.save()
    return company


@pytest.fixture
def public_profile_cars():
    company = Company(**default_public_profile_data)
    company.number = '0123456D'
    company.is_published = True
    company.sectors = ['AUTOMOTIVE']
    company.save()
    return company


@pytest.fixture
def public_profile_smart_cars():
    company = Company(**default_public_profile_data)
    company.number = '0123456E'
    company.is_published = True
    company.sectors = ['SOFTWARE_AND_COMPUTER_SERVICES', 'AUTOMOTIVE']
    company.save()
    return company


@pytest.fixture
def supplier_case_study(case_study_data, company):
    return CompanyCaseStudy.objects.create(
        title=case_study_data['title'],
        description=case_study_data['description'],
        sector=case_study_data['sector'],
        website=case_study_data['website'],
        year=case_study_data['year'],
        keywords=case_study_data['keywords'],
        testimonial=case_study_data['testimonial'],
        company=company,
    )


@pytest.fixture
def supplier(company):
    return Supplier.objects.create(
        sso_id=2,
        company_email='someone@example.com',
        company=company,
    )


@pytest.mark.django_db
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_update(
    company_data, api_client, supplier, company
):
    url = reverse('company', kwargs={'sso_id': supplier.sso_id})

    response = api_client.patch(url, company_data)
    instance = Company.objects.get(number=response.data['number'])

    assert response.status_code == http.client.OK
    assert instance.number == '01234567'
    assert instance.name == 'Test Company'
    assert instance.website == 'http://example.com'
    assert instance.description == 'Company description'
    assert instance.export_status == choices.EXPORT_STATUSES[1][0]
    assert instance.date_of_creation == datetime.date(2010, 10, 10)
    assert instance.revenue == Decimal('100000.00')


@pytest.mark.django_db
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_create(
    case_study_data, api_client, supplier, company
):
    url = reverse('company-case-study', kwargs={'sso_id': supplier.sso_id})

    response = api_client.post(url, case_study_data, format='multipart')
    instance = CompanyCaseStudy.objects.get(pk=response.data['pk'])

    assert response.status_code == http.client.CREATED
    assert instance.testimonial == case_study_data['testimonial']
    assert instance.website == case_study_data['website']
    assert instance.company == company
    assert instance.year == case_study_data['year']
    assert instance.description == case_study_data['description']
    assert instance.title == case_study_data['title']
    assert instance.sector == case_study_data['sector']
    assert instance.keywords == case_study_data['keywords']


@pytest.mark.django_db
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_update(supplier_case_study, supplier, api_client):
    url = reverse(
        'company-case-study-detail',
        kwargs={'sso_id': supplier.sso_id, 'pk': supplier_case_study.pk}
    )
    data = {'year': '2015'}

    assert supplier_case_study.year != data['year']

    response = api_client.patch(url, data, format='multipart')
    supplier_case_study.refresh_from_db()

    assert response.status_code == http.client.OK
    assert supplier_case_study.year == data['year']


@pytest.mark.django_db
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_delete(supplier_case_study, supplier, api_client):
    pk = supplier_case_study.pk
    url = reverse(
        'company-case-study-detail', kwargs={
            'sso_id': supplier.sso_id, 'pk': pk
        }
    )

    response = api_client.delete(url)

    assert response.status_code == http.client.NO_CONTENT
    assert CompanyCaseStudy.objects.filter(pk=pk).exists() is False


@pytest.mark.django_db
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
def test_company_case_study_get(
        supplier_case_study, supplier, api_client
):
    pk = supplier_case_study.pk
    url = reverse(
        'company-case-study-detail', kwargs={
            'sso_id': supplier.sso_id, 'pk': pk
        }
    )

    response = api_client.get(url)
    data = response.json()

    assert response.status_code == http.client.OK
    assert data['testimonial'] == supplier_case_study.testimonial
    assert data['website'] == supplier_case_study.website
    assert data['year'] == supplier_case_study.year
    assert data['description'] == supplier_case_study.description
    assert data['title'] == supplier_case_study.title
    assert data['sector'] == supplier_case_study.sector
    assert data['keywords'] == supplier_case_study.keywords
    assert isinstance(data['company'], dict)
    assert data['company']['id'] == supplier_case_study.company.pk


@pytest.mark.django_db
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
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
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
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
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
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
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
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
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
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
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
def test_verify_company_with_code(api_client, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with patch('requests.post'):
        company = Company.objects.create(**{
            "number": "11234567",
            "name": 'Test Company',
            "website": "http://example.com",
            "description": "Company description",
            "export_status": choices.EXPORT_STATUSES[1][0],
            "date_of_creation": "2010-10-10",
            "revenue": '100000.00',
            "contact_details": {
                'title': 'test_title',
                'firstname': 'test_firstname',
                'lastname': 'test_lastname',
                'address_line_1': 'test_address_line_1',
                'address_line_2': 'test_address_line_2',
                'locality': 'test_locality',
                'postal_code': 'test_postal_code',
                'country': 'test_country',
            }
        })

    supplier = Supplier.objects.create(
        sso_id=3,
        company_email='test@example.com',
        company=company,
    )
    company.refresh_from_db()
    assert company.verification_code

    url = reverse('company-verify', kwargs={'sso_id': supplier.sso_id})
    response = api_client.post(
        url, {'code': company.verification_code}, format='json'
    )

    assert response.status_code == http.client.OK

    company.refresh_from_db()
    assert company.verified_with_code is True


@pytest.mark.django_db
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
def test_verify_company_with_code_invalid_code(api_client, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with patch('requests.post'):
        company = Company.objects.create(**{
            "number": "11234567",
            "name": 'Test Company',
            "website": "http://example.com",
            "description": "Company description",
            "export_status": choices.EXPORT_STATUSES[1][0],
            "date_of_creation": "2010-10-10",
            "revenue": '100000.00',
            "contact_details": {
                'title': 'test_title',
                'firstname': 'test_firstname',
                'lastname': 'test_lastname',
                'address_line_1': 'test_address_line_1',
                'address_line_2': 'test_address_line_2',
                'locality': 'test_locality',
                'postal_code': 'test_postal_code',
                'country': 'test_country',
            }
        })

    supplier = Supplier.objects.create(
        sso_id=3,
        company_email='test@example.com',
        company=company,
    )
    company.refresh_from_db()
    assert company.verification_code

    url = reverse('company-verify', kwargs={'sso_id': supplier.sso_id})
    response = api_client.post(
        url, {'code': 'invalid'}, format='json'
    )

    assert response.status_code == http.client.BAD_REQUEST

    company.refresh_from_db()
    assert company.verified_with_code is False


@pytest.mark.django_db
@patch('signature.permissions.SignaturePermission.has_permission', Mock)
def test_verify_company_with_code_invalid_user(api_client, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with patch('requests.post'):
        company = Company.objects.create(**{
            "number": "11234567",
            "name": 'Test Company',
            "website": "http://example.com",
            "description": "Company description",
            "export_status": choices.EXPORT_STATUSES[1][0],
            "date_of_creation": "2010-10-10",
            "revenue": '100000.00',
            "contact_details": {
                'title': 'test_title',
                'firstname': 'test_firstname',
                'lastname': 'test_lastname',
                'address_line_1': 'test_address_line_1',
                'address_line_2': 'test_address_line_2',
                'locality': 'test_locality',
                'postal_code': 'test_postal_code',
                'country': 'test_country',
            }
        })

    Supplier.objects.create(
        sso_id=3,
        company_email='test@example.com',
        company=company,
    )
    company.refresh_from_db()
    assert company.verification_code

    url = reverse('company-verify', kwargs={'sso_id': 12345})
    response = api_client.post(
        url, {'code': company.verification_code}, format='json'
    )

    assert response.status_code == http.client.NOT_FOUND

    company.refresh_from_db()
    assert company.verified_with_code is False
