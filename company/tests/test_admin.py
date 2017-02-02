from unittest import TestCase

from freezegun import freeze_time
import pytest

from django.test import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from company.models import CompanyCaseStudy
from company.tests.factories import CompanyCaseStudyFactory


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
            '{company_id},2012-01-14 12:00:00+00:00,{description},{id},,,,,,,,'
            '2012-01-14 12:00:00+00:00,,,,,,,{title},,'
        ).format(
            company_id=case_study.company_id,
            description=case_study.description,
            title=case_study.title,
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
            '2012-01-14 12:00:00+00:00,,,,,,,{title},,'
        ).format(
            company_id=case_studies[2].company_id,
            description=case_studies[2].description,
            title=case_studies[2].title,
            id=case_studies[2].id,
        )

        row_two = (
            '{company_id},2012-01-14 12:00:00+00:00,{description},{id},,,,,,,,'
            '2012-01-14 12:00:00+00:00,,,,,,,{title},,'
        ).format(
            company_id=case_studies[1].company_id,
            description=case_studies[1].description,
            title=case_studies[1].title,
            id=case_studies[1].id,
        )

        row_three = (
            '{company_id},2012-01-14 12:00:00+00:00,{description},{id},,,,,,,,'
            '2012-01-14 12:00:00+00:00,,,,,,,{title},,'
        ).format(
            company_id=case_studies[0].company_id,
            description=case_studies[0].description,
            title=case_studies[0].title,
            id=case_studies[0].id,
        )

        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == self.headers
        assert actual[1] == row_one
        assert actual[2] == row_two
        assert actual[3] == row_three
