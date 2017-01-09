import http
from unittest import TestCase

from freezegun import freeze_time
import pytest

from django.test import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from company.models import Company, CompanyCaseStudy
from company.admin import PublishByCompanyHouseNumberForm
from company.tests.factories import CompanyFactory, CompanyCaseStudyFactory


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
        companies = CompanyFactory.create_batch(5, is_published=False)
        published_company = CompanyFactory(is_published=True)
        numbers = '{num1},{num2}'.format(
            num1=companies[0].number, num2=companies[3].number)

        response = self.client.post(
            reverse('admin:company_company_publish'),
            {'company_numbers': numbers},
        )

        assert response.status_code == http.client.FOUND
        assert response.url == reverse('admin:company_company_changelist')

        published = Company.objects.filter(is_published=True).values_list(
            'number', flat=True)
        assert len(published) == 3
        assert companies[0].number in published
        assert companies[3].number in published
        assert published_company.number in published

        unpublished = Company.objects.filter(is_published=False).values_list(
            'number', flat=True)
        assert len(unpublished) == 3
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
    form = PublishByCompanyHouseNumberForm(data=data)

    assert form.is_valid() is False
    msg = COMPANY_DOESNT_EXIST_MSG + '12345678, 23456789, 34567890'
    assert form.errors['company_numbers'] == [msg]

    # some exist, some don't
    company = CompanyFactory()
    data = {
        'company_numbers': '{num},23456789'.format(num=company.number)
    }
    form = PublishByCompanyHouseNumberForm(data=data)

    assert form.is_valid() is False
    msg = COMPANY_DOESNT_EXIST_MSG + '23456789'
    assert form.errors['company_numbers'] == [msg]


@pytest.mark.django_db
def test_companies_publish_form_handles_whitespace():
    companies = CompanyFactory.create_batch(3)
    data = '	{num1},{num2} , {num3},'.format(
        num1=companies[0].number, num2=companies[1].number,
        num3=companies[2].number)
    form = PublishByCompanyHouseNumberForm(data={'company_numbers': data})

    assert form.is_valid() is True


@pytest.mark.django_db
class DownloadCaseStudyCSVTestCase(TestCase):

    headers = (
        'company,created,description,id,image_one,image_one_caption,'
        'image_three,image_three_caption,image_two,image_two_caption,'
        'keywords,modified,sector,short_summary,testimonial,'
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
            '1,2012-01-14 12:00:00+00:00,{description},1,,,,,,,,'
            '2012-01-14 12:00:00+00:00,,,,,,,{title},,'
        ).format(
            description=case_study.description,
            title=case_study.title,

        )
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == self.headers
        assert actual[1] == row_one

    def test_download_csv_multiple_multiple_case_studies(self):
        CompanyCaseStudyFactory.create_batch(3)

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

        company_one = CompanyCaseStudy.objects.get(id=3)
        row_one = (
            '3,2012-01-14 12:00:00+00:00,{description},3,,,,,,,,2012-01-14'
            ' 12:00:00+00:00,,,,,,,{title},,'
        ).format(
            description=company_one.description,
            title=company_one.title
        )

        company_two = CompanyCaseStudy.objects.get(id=2)
        row_two = (
            '2,2012-01-14 12:00:00+00:00,{description},2,,,,,,,,2012-01-14'
            ' 12:00:00+00:00,,,,,,,{title},,'
        ).format(
            description=company_two.description,
            title=company_two.title
        )

        company_three = CompanyCaseStudy.objects.get(id=1)
        row_three = (
            '1,2012-01-14 12:00:00+00:00,{description},1,,,,,,,,2012-01-14'
            ' 12:00:00+00:00,,,,,,,{title},,'
        ).format(
            description=company_three.description,
            title=company_three.title
        )

        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == self.headers
        assert actual[1] == row_one
        assert actual[2] == row_two
        assert actual[3] == row_three
