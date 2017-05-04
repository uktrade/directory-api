import datetime
import http
from io import BytesIO
from unittest.mock import patch, Mock
from unittest import TestCase

from django.core.urlresolvers import reverse
from django.test import Client

from directory_validators.constants import choices
from elasticsearch_dsl.connections import connections
import pytest
from freezegun import freeze_time
from rest_framework.test import APIClient
from rest_framework import status
from PIL import Image, ImageDraw

from company.models import Company, CompanyCaseStudy
from company.tests import (
    MockInvalidSerializer,
    MockValidSerializer,
    VALID_REQUEST_DATA,
)
from company.tests.factories import CompanyFactory, CompanyCaseStudyFactory
from user.models import User as Supplier


default_public_profile_data = {
    'name': 'private company',
    'website': 'http://example.com',
    'description': 'Company description',
    'export_status': choices.EXPORT_STATUSES[1][0],
    'date_of_creation': '2010-10-10',
    'email_address': 'thing@example.com',
    'verified_with_code': True,
}


class CompanyViewsTests(TestCase):

    def setUp(self):
        self.client = Client()

        self.signature_permission_mock = patch(
            'api.signature.SignatureCheckPermission.has_permission'
        )

        self.signature_permission_mock.start()

    def tearDown(self):
        self.signature_permission_mock.stop()

    @freeze_time('2016-11-23T11:21:10.977518Z')
    @pytest.mark.django_db
    def test_company_retrieve_view(self):
        client = APIClient()
        company = CompanyFactory(
            name='Test Company', date_of_creation=datetime.date(2000, 10, 10))
        supplier = Supplier.objects.create(
            sso_id=1,
            company_email='harry.potter@hogwarts.com',
            company=company,
        )

        response = client.get(reverse(
            'company', kwargs={'sso_id': supplier.sso_id}
        ))

        expected = {
            'date_of_creation': '2000-10-10',
            'email_address': company.email_address,
            'email_full_name': company.email_full_name,
            'employees': company.employees,
            'facebook_url': company.facebook_url,
            'has_valid_address': True,
            'id': str(company.id),
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
            'country': company.country,
            'mobile_number': company.mobile_number,
            'address_line_1': company.address_line_1,
            'address_line_2': company.address_line_2,
            'postal_full_name': company.postal_full_name,
            'number': company.number,
            'website': company.website,
            'description': company.description,
            'export_status': company.export_status,
            'locality': company.locality,
            'name': 'Test Company',
            'postal_code': company.postal_code,
        }
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @pytest.mark.django_db
    def test_company_retrieve_view_404(self):
        client = APIClient()
        company = CompanyFactory()
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
        company = CompanyFactory(
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
            'email_address': company.email_address,
            'email_full_name': company.email_full_name,
            'employees': company.employees,
            'facebook_url': company.facebook_url,
            'has_valid_address': True,
            'id': str(company.id),
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
        }
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @freeze_time('2016-11-23T11:21:10.977518Z')
    @pytest.mark.django_db
    def test_company_update_view_with_patch(self):
        client = APIClient()
        company = CompanyFactory(
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
            'email_address': company.email_address,
            'email_full_name': company.email_full_name,
            'employees': company.employees,
            'facebook_url': company.facebook_url,
            'has_valid_address': True,
            'id': str(company.id),
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
        }
        expected.update(VALID_REQUEST_DATA)
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == expected

    @freeze_time('2016-11-23T11:21:10.977518Z')
    @pytest.mark.django_db
    def test_company_update_view_with_put_ignores_modified(self):
        client = APIClient()
        company = CompanyFactory(
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
        company = CompanyFactory(
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
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
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
        'export_status': choices.EXPORT_STATUSES[1][0],
        'date_of_creation': '2010-10-10',
    }


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def company():
    return Company.objects.create(
        verified_with_code=True,
        email_address='test@example.com',
        **VALID_REQUEST_DATA
    )


@pytest.fixture
def private_profile():
    company = Company(**default_public_profile_data)
    company.number = '0123456A'
    company.verified_with_code = False
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
def public_profile_with_case_study():
    company = CompanyFactory(is_published=True)
    CompanyCaseStudyFactory(company=company)
    return company


@pytest.fixture
def public_profile_with_case_studies():
    company = CompanyFactory(is_published=True)
    CompanyCaseStudyFactory(company=company)
    CompanyCaseStudyFactory(company=company)
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


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
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


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_create(
    case_study_data, api_client, supplier, company
):
    url = reverse('company-case-study', kwargs={'sso_id': supplier.sso_id})

    response = api_client.post(url, case_study_data, format='multipart')
    assert response.status_code == http.client.CREATED

    instance = CompanyCaseStudy.objects.get(pk=response.data['pk'])
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_create_invalid_image(
    api_client, supplier, company
):
    url = reverse('company-case-study', kwargs={'sso_id': supplier.sso_id})

    case_study_data = {
        'company': company.pk,
        'title': 'a title',
        'description': 'a description',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
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
    response = api_client.post(url, case_study_data, format='multipart')

    assert response.status_code == http.client.BAD_REQUEST


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_create_not_an_image(
    video, api_client, supplier, company
):
    url = reverse('company-case-study', kwargs={'sso_id': supplier.sso_id})

    case_study_data = {
        'company': company.pk,
        'title': 'a title',
        'description': 'a description',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
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
    response = api_client.post(url, case_study_data, format='multipart')

    assert response.status_code == http.client.BAD_REQUEST


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_create_company_not_published(
    video, api_client, supplier
):

    company = Company.objects.create(
        number='01234567',
        export_status=choices.EXPORT_STATUSES[1][0],
        is_published=False
    )

    supplier = Supplier.objects.create(
        sso_id=1,
        company_email='harry.potter@hogwarts.com',
        company=company,
    )

    url = reverse('company-case-study', kwargs={'sso_id': supplier.sso_id})

    case_study_data = {
        'company': company.pk,
        'title': 'a title',
        'description': 'a description',
        'sector': choices.COMPANY_CLASSIFICATIONS[1][0],
        'website': 'http://www.example.com',
        'keywords': 'good, great',
        'image_one': get_test_image(extension="PNG"),
        'testimonial': 'very nice',
        'testimonial_name': 'Lord Voldemort',
        'testimonial_job_title': 'Evil overlord',
        'testimonial_company': 'Death Eaters',
    }
    response = api_client.post(url, case_study_data, format='multipart')

    assert response.status_code == http.client.CREATED

    url = reverse(
        'public-case-study-detail', kwargs={'pk': response.data['pk']}
    )
    response = api_client.get(url)

    assert response.status_code == http.client.NOT_FOUND


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
@patch('django.core.files.storage.Storage.save', mock_save)
def test_company_case_study_update(supplier_case_study, supplier, api_client):
    url = reverse(
        'company-case-study-detail',
        kwargs={'sso_id': supplier.sso_id, 'pk': supplier_case_study.pk}
    )
    data = {'title': '2015'}

    assert supplier_case_study.title != data['title']

    response = api_client.patch(url, data, format='multipart')
    supplier_case_study.refresh_from_db()

    assert response.status_code == http.client.OK
    assert supplier_case_study.title == data['title']


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_verify_company_with_code(api_client, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with patch('requests.post'):
        company = Company.objects.create(**{
            'number': '11234567',
            'name': 'Test Company',
            'website': 'http://example.com',
            'description': 'Company description',
            'export_status': choices.EXPORT_STATUSES[1][0],
            'date_of_creation': '2010-10-10',
            'postal_full_name': 'test_full_name',
            'address_line_1': 'test_address_line_1',
            'address_line_2': 'test_address_line_2',
            'locality': 'test_locality',
            'postal_code': 'test_postal_code',
            'country': 'test_country',
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_verify_company_with_code_invalid_code(api_client, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with patch('requests.post'):
        company = Company.objects.create(**{
            'number': '11234567',
            'name': 'Test Company',
            'website': 'http://example.com',
            'description': 'Company description',
            'export_status': choices.EXPORT_STATUSES[1][0],
            'date_of_creation': '2010-10-10',
            'postal_full_name': 'test_full_name',
            'address_line_1': 'test_address_line_1',
            'address_line_2': 'test_address_line_2',
            'locality': 'test_locality',
            'postal_code': 'test_postal_code',
            'country': 'test_country',
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
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_verify_company_with_code_invalid_user(api_client, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with patch('requests.post'):
        company = Company.objects.create(**{
            'number': '11234567',
            'name': 'Test Company',
            'website': 'http://example.com',
            'description': 'Company description',
            'export_status': choices.EXPORT_STATUSES[1][0],
            'date_of_creation': '2010-10-10',
            'postal_full_name': 'test_full_name',
            'address_line_1': 'test_address_line_1',
            'address_line_2': 'test_address_line_2',
            'locality': 'test_locality',
            'postal_code': 'test_postal_code',
            'country': 'test_country',
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


@patch('company.views.CompanySearchAPIView.get_search_results')
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_company_search(mock_get_search_results, api_client):
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
    mock_get_search_results.assert_called_once_with(
        term='bones', page=1, size=10,
    )


@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_company_paginate_first_page(api_client):
    # [page number, expected_start]
    params = [
        [1, 0],
        [2, 5],
        [3, 10],
        [4, 15],
        [5, 20],
        [6, 25],
        [7, 30],
        [8, 35],
        [9, 40],
    ]
    es = connections.get_connection('default')
    for page, expected_start in params:
        with patch.object(es, 'search', return_value={}) as mock_search:
            data = {'term': 'bones', 'page': page, 'size': 5}
            api_client.get(reverse('company-search'), data=data)
            mock_search.assert_called_once_with(
                body={
                    'size': 5,
                    'from': expected_start,
                    'query': {
                        'match': {
                            '_all': 'bones'
                        }
                    }
                },
                doc_type=['company_doc_type'],
                index=['company']
            )
