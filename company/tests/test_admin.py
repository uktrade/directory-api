import http
import os
from unittest import TestCase

from freezegun import freeze_time
import pytest

from django.conf import settings
from django.test import Client
from django.contrib.auth.models import User
from django.core.signing import Signer
from django.core.urlresolvers import reverse

from company import constants, admin
from company.models import Company, CompanyCaseStudy
from company.tests.factories import CompanyFactory, CompanyCaseStudyFactory
from enrolment.models import PreVerifiedEnrolment


COMPANY_DOESNT_EXIST_MSG = (
    'Some companies in this data set are not in the db: '
)


@pytest.mark.django_db
class PublishCompaniesTestCase(TestCase):

    def setUp(self):
        superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='test'
        )
        self.client = Client()
        self.client.force_login(superuser)

    def test_superuser_can_access_company_publish_view_get(self):
        response = self.client.get(reverse('admin:company_company_publish'))

        assert response.status_code == http.client.OK

    def test_companies_in_post_set_to_published(self):
        companies = CompanyFactory.create_batch(
            7,
            is_published_investment_support_directory=False,
            is_published_find_a_supplier=False,
        )
        published_company_isd = CompanyFactory(
            is_published_investment_support_directory=True
        )

        numbers = '{num1},{num2}'.format(
            num1=companies[0].number, num2=companies[3].number)

        response = self.client.post(
            reverse('admin:company_company_publish'),
            {'company_numbers': numbers,
             'directories': [
                 'investment_support_directory',
                 'find_a_supplier'
             ],
             },
        )

        assert response.status_code == http.client.FOUND
        assert response.url == reverse('admin:company_company_changelist')

        published_isd = Company.objects.filter(
            is_published_investment_support_directory=True
        ).values_list('number', flat=True)

        assert len(published_isd) == 3
        assert companies[0].number in published_isd
        assert companies[3].number in published_isd
        assert published_company_isd.number in published_isd

        published_fas = Company.objects.filter(
            is_published_find_a_supplier=True
        ).values_list('number', flat=True)

        assert len(published_fas) == 2
        assert companies[0].number in published_fas
        assert companies[3].number in published_fas

        unpublished = Company.objects.filter(
            is_published_investment_support_directory=False,
            is_published_find_a_supplier=False,
        ).values_list('number', flat=True)
        assert len(unpublished) == 5
        assert companies[1].number in unpublished
        assert companies[2].number in unpublished
        assert companies[4].number in unpublished


@pytest.mark.django_db
class CompanyAdminAuthTestCase(TestCase):

    def setUp(self):
        self.client = Client()

    def test_nonsuperuser_cannot_access_company_publish_view_get(self):
        user = User.objects.create_user(
            username='user', email='user@example.com', password='test'
        )
        self.client.force_login(user)
        url = reverse('admin:company_company_publish')

        response = self.client.get(url)

        assert response.status_code == http.client.FOUND
        assert response.url == '/admin/login/?next={redirect_to}'.format(
            redirect_to=url)

    def test_nonsuperuser_cannot_access_company_publish_view_post(self):
        company = CompanyFactory()
        user = User.objects.create_user(
            username='user', email='user@example.com', password='test'
        )
        self.client.force_login(user)
        url = reverse('admin:company_company_publish')

        response = self.client.post(
            url, {'company_numbers': company.number})

        assert response.status_code == http.client.FOUND
        assert response.url == '/admin/login/?next={redirect_to}'.format(
            redirect_to=url)

    def test_guest_cannot_access_company_publish_view_get(self):
        url = reverse('admin:company_company_publish')

        response = self.client.get(url)

        assert response.status_code == http.client.FOUND
        assert response.url == '/admin/login/?next={redirect_to}'.format(
            redirect_to=url)

    def test_guest_cannot_access_company_publish_view_post(self):
        url = reverse('admin:company_company_publish')
        company = CompanyFactory()

        response = self.client.post(
            url, {'company_numbers': company.number})

        assert response.status_code == http.client.FOUND
        assert response.url == '/admin/login/?next={redirect_to}'.format(
            redirect_to=url)


@pytest.mark.django_db
def test_companies_publish_form_doesnt_allow_numbers_that_dont_exist():
    # all don't exist
    data = {
        'company_numbers': '12345678,23456789,34567890'
    }
    form = admin.PublishByCompanyHouseNumberForm(data=data)

    assert form.is_valid() is False
    msg = COMPANY_DOESNT_EXIST_MSG + '12345678, 23456789, 34567890'
    assert form.errors['company_numbers'] == [msg]

    # some exist, some don't
    company = CompanyFactory()
    data = {
        'company_numbers': '{num},23456789'.format(num=company.number)
    }
    form = admin.PublishByCompanyHouseNumberForm(data=data)

    assert form.is_valid() is False
    msg = COMPANY_DOESNT_EXIST_MSG + '23456789'
    assert form.errors['company_numbers'] == [msg]


@pytest.mark.django_db
def test_companies_publish_form_handles_whitespace():
    companies = CompanyFactory.create_batch(3)
    data = '    {num1},{num2} , {num3},'.format(
        num1=companies[0].number, num2=companies[1].number,
        num3=companies[2].number)
    form = admin.PublishByCompanyHouseNumberForm(
        data={
            'company_numbers': data,
            'directories': ['investment_support_directory']
        }
    )

    assert form.is_valid() is True


@pytest.mark.django_db
class DownloadCaseStudyCSVTestCase(TestCase):

    headers = (
        'company,created,description,id,image_one,image_one_caption,'
        'image_three,image_three_caption,image_two,image_two_caption,'
        'keywords,modified,sector,short_summary,slug,testimonial,'
        'testimonial_company,testimonial_job_title,testimonial_name,'
        'title,video_one,website'
    )

    def setUp(self):
        superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='test'
        )
        self.client = Client()
        self.client.force_login(superuser)

        self.freezer = freeze_time("2012-01-14 12:00:00")
        self.freezer.start()

    def tearDown(self):
        self.freezer.stop()

    def test_download_csv_single_case_study(self):
        case_study = CompanyCaseStudyFactory()

        data = {
            'action': 'download_csv',
            '_selected_action': CompanyCaseStudy.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:company_companycasestudy_changelist'),
            data,
            follow=True
        )

        row_one = (
            '{company_id},2012-01-14 12:00:00+00:00,{description},{id},,,,,,,,'
            '2012-01-14 12:00:00+00:00,,,{slug},,,,,{title},,'
        ).format(
            company_id=case_study.company_id,
            description=case_study.description,
            title=case_study.title,
            slug=case_study.slug,
            id=case_study.id,

        )
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == self.headers
        assert actual[1] == row_one

    def test_download_csv_multiple_multiple_case_studies(self):
        case_studies = CompanyCaseStudyFactory.create_batch(3)
        data = {
            'action': 'download_csv',
            '_selected_action': CompanyCaseStudy.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:company_companycasestudy_changelist'),
            data,
            follow=True
        )

        row_one = (
            '{company_id},2012-01-14 12:00:00+00:00,{description},{id},,,,,,,,'
            '2012-01-14 12:00:00+00:00,,,{slug},,,,,{title},,'
        ).format(
            company_id=case_studies[2].company_id,
            description=case_studies[2].description,
            slug=case_studies[2].slug,
            title=case_studies[2].title,
            id=case_studies[2].id,
        )

        row_two = (
            '{company_id},2012-01-14 12:00:00+00:00,{description},{id},,,,,,,,'
            '2012-01-14 12:00:00+00:00,,,{slug},,,,,{title},,'
        ).format(
            company_id=case_studies[1].company_id,
            description=case_studies[1].description,
            slug=case_studies[1].slug,
            title=case_studies[1].title,
            id=case_studies[1].id,
        )

        row_three = (
            '{company_id},2012-01-14 12:00:00+00:00,{description},{id},,,,,,,,'
            '2012-01-14 12:00:00+00:00,,,{slug},,,,,{title},,'
        ).format(
            company_id=case_studies[0].company_id,
            description=case_studies[0].description,
            slug=case_studies[0].slug,
            title=case_studies[0].title,
            id=case_studies[0].id,
        )

        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == self.headers
        assert actual[1] == row_one
        assert actual[2] == row_two
        assert actual[3] == row_three

    def test_create_companies_form_success(self):
        file_path = os.path.join(
            settings.BASE_DIR,
            'company/tests/fixtures/valid-companies-upload.csv'
        )

        response = self.client.post(
            reverse('admin:company_company_enrol'),
            {
                'generated_for': constants.UK_ISD,
                'csv_file': open(file_path, 'rb'),
            }
        )

        assert response.status_code == 200

        assert Company.objects.count() == 2
        company_one, company_two = Company.objects.all()

        assert company_one.name == 'Example Compass'
        assert company_one.address_line_1 == ''
        assert company_one.address_line_2 == ''
        assert company_one.postal_code == ''
        assert company_one.email_address == ''
        assert company_one.mobile_number == '55555555555'
        assert company_one.number == '12355434'
        assert company_one.website == 'http://www.example-compass.co.uk'
        assert company_one.twitter_url == 'https://www.twitter.com/one'
        assert company_one.facebook_url == 'https://www.facebook.com/one'
        assert company_one.linkedin_url == (
            'https://www.linkedin.com/company/one'
        )
        assert company_one.company_type == Company.COMPANIES_HOUSE
        assert company_one.is_uk_isd_company is True

        assert company_two.name == 'Example Associates Ltd'
        assert company_two.address_line_1 == 'Example Business Centre'
        assert company_two.address_line_2 == 'Example barn Farm'
        assert company_two.postal_code == 'IG22 0PQ'
        assert company_two.email_address == ''
        assert company_two.mobile_number == '6666666'
        assert company_two.number.startswith('ST')
        assert company_two.website == 'http://www.example-asscoiates.com'
        assert company_two.twitter_url == 'https://www.twitter.com/two'
        assert company_two.facebook_url == 'https://www.facebook.com/two'
        assert company_two.linkedin_url == (
            'https://www.linkedin.com/company/two'
        )
        assert company_two.company_type == Company.SOLE_TRADER
        assert company_two.is_uk_isd_company is True

        pre_verified_queryset = PreVerifiedEnrolment.objects.all()
        assert len(pre_verified_queryset) == 2

        assert pre_verified_queryset[0].company_number == company_one.number
        assert pre_verified_queryset[0].generated_for == constants.UK_ISD
        assert pre_verified_queryset[1].company_number == company_two.number
        assert pre_verified_queryset[1].generated_for == constants.UK_ISD

        signer = Signer()
        assert response.context_data['created_companies'] == [
            {
                'name': 'Example Compass',
                'number': company_one.number,
                'email_address': 'one@example.com',
                'url': (
                    'http://profile.trade.great:8006/profile/enrol/'
                    'pre-verified/?key=' + signer.sign(company_one.number)
                )
            },
            {
                'name': 'Example Associates Ltd',
                'number': company_two.number,
                'email_address': 'two@example.com',
                'url': (
                    'http://profile.trade.great:8006/profile/enrol/'
                    'pre-verified/?key=' + signer.sign(company_two.number)
                )
            }
        ]

    def test_create_companies_form_invalid_enrolment(self):
        file_path = os.path.join(
            settings.BASE_DIR,
            'company/tests/fixtures/invalid-companies-upload.csv'
        )

        response = self.client.post(
            reverse('admin:company_company_enrol'),
            {
                'csv_file': open(file_path, 'rb'),
                'generated_for': constants.UK_ISD,
            }
        )

        assert response.status_code == 200
        assert response.context_data['form'].errors == {
            'csv_file': ['[Row 3] {"name": ["This field is required."]}']
        }

    def test_create_companies_form_existing(self):

        company = CompanyFactory(number=12355434)
        assert company.is_uk_isd_company is False

        file_path = os.path.join(
            settings.BASE_DIR,
            'company/tests/fixtures/valid-companies-upload.csv'
        )

        response = self.client.post(
            reverse('admin:company_company_enrol'),
            {
                'generated_for': constants.UK_ISD,
                'csv_file': open(file_path, 'rb'),
            }
        )

        assert response.status_code == 200
        assert Company.objects.count() == 2
        company.refresh_from_db()

        assert company.is_uk_isd_company is True


def test_company_search_fields_exist():
    """It will raise FieldError if a field don't exist."""
    for fieldname in admin.CompanyAdmin.search_fields:
        query_key = '{}__icontains'.format(fieldname)
        query = {query_key: 'foo'}
        Company.objects.filter(**query)


def test_company_case_study_search_fields_exist():
    """It will raise FieldError if a field don't exist."""
    for fieldname in admin.CompanyCaseStudyAdmin.search_fields:
        query_key = '{}__icontains'.format(fieldname)
        query = {query_key: 'foo'}
        CompanyCaseStudy.objects.filter(**query)
