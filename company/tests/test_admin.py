from collections import OrderedDict
import http
import os
from unittest import TestCase
from unittest.mock import patch

from directory_constants import company_types
from freezegun import freeze_time
import pytest

from django.conf import settings
from django.test import Client
from django.contrib.auth.models import User
from django.core.signing import Signer
from django.urls import reverse

from company import admin, constants, models
from company.tests import VALID_REQUEST_DATA, VALID_SUPPLIER_REQUEST_DATA
from company.tests.factories import CompanyFactory, CompanyCaseStudyFactory
from enrolment.models import PreVerifiedEnrolment


COMPANY_DATA = VALID_REQUEST_DATA.copy()
SUPPLIER_DATA = VALID_SUPPLIER_REQUEST_DATA.copy()
COMPANY_DOESNT_EXIST_MSG = 'Some companies in this data set are not in the db: '


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
        published_company_isd = CompanyFactory(is_published_investment_support_directory=True)

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

        published_isd = models.Company.objects.filter(
            is_published_investment_support_directory=True
        ).values_list('number', flat=True)

        assert len(published_isd) == 3
        assert companies[0].number in published_isd
        assert companies[3].number in published_isd
        assert published_company_isd.number in published_isd

        published_fas = models.Company.objects.filter(
            is_published_find_a_supplier=True
        ).values_list('number', flat=True)

        assert len(published_fas) == 2
        assert companies[0].number in published_fas
        assert companies[3].number in published_fas

        unpublished = models.Company.objects.filter(
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
        assert response.status_code == 401

    def test_nonsuperuser_cannot_access_company_publish_view_post(self):
        company = CompanyFactory()
        user = User.objects.create_user(username='user', email='user@example.com', password='test')
        self.client.force_login(user)
        url = reverse('admin:company_company_publish')

        response = self.client.post(
            url, {'company_numbers': company.number})

        assert response.status_code == 401

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
            '_selected_action': models.CompanyCaseStudy.objects.all().values_list(
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
            '_selected_action': models.CompanyCaseStudy.objects.all().values_list(
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

        assert models.Company.objects.count() == 2
        company_one, company_two = models.Company.objects.all()

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
        assert company_one.company_type == company_types.COMPANIES_HOUSE
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
        assert company_two.company_type == company_types.SOLE_TRADER
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

    def test_upload_expertise_companies_form_success(self):

        company_1 = CompanyFactory(
            name='Test 1',
        )
        company_2 = CompanyFactory(
            number='74897421',
        )
        company_3 = CompanyFactory(
            name='Test 3',
            number='23242314',
            expertise_products_services={},
        )
        CompanyFactory(
            name='Test 4',
            number='',
        )
        CompanyFactory(
            name='Test 4',
        )

        file_path = os.path.join(
            settings.BASE_DIR,
            'company/tests/fixtures/expertise-company-upload.csv'
        )

        response = self.client.post(
            reverse('admin:upload_company_expertise'),
            {
                'csv_file': open(file_path, 'rb'),
            }
        )

        company_1.refresh_from_db()
        company_2.refresh_from_db()
        company_3.refresh_from_db()

        assert company_1.expertise_products_services == (
            {
             'Finance': ['Raising capital'],
             'Management Consulting': ['Workforce development'],
             'Human Resources': ['Sourcing and hiring', 'Succession planning'],
             'Publicity': ['Social media'],
             'Business Support': ['Planning consultants']
            }
        )
        assert company_2.expertise_products_services == (
            {
                'Finance': ['Insurance']
            }
        )
        assert company_3.expertise_products_services == {
            'Legal': ['Immigration'],
            'Business Support': ['Facilities (such as WiFI or electricity)']
        }
        assert response.context['errors'] == [
            '[Row 3] "Unable to find following products & services '
            '[\'Unkown Skill\']"',
            '[Row 5] "More then one company returned - '
            'Name:Test 4 Number:00000000)"',
            '[Row 6] "Company not found - Name:Test 9999 Number:00000000)"'
        ]
        assert len(response.context['updated_companies']) == 3

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
        assert models.Company.objects.count() == 2
        company.refresh_from_db()

        assert company.is_uk_isd_company is True


def test_company_search_fields_exist():
    """It will raise FieldError if a field don't exist."""
    for fieldname in admin.CompanyAdmin.search_fields:
        query_key = '{}__icontains'.format(fieldname)
        query = {query_key: 'foo'}
        models.Company.objects.filter(**query)


def test_company_case_study_search_fields_exist():
    """It will raise FieldError if a field don't exist."""
    for fieldname in admin.CompanyCaseStudyAdmin.search_fields:
        query_key = '{}__icontains'.format(fieldname)
        query = {query_key: 'foo'}
        models.CompanyCaseStudy.objects.filter(**query)


@pytest.mark.django_db
class DownloadCSVTestCase(TestCase):

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

    def test_download_csv(self):
        company = models.Company.objects.create(
            **COMPANY_DATA,
            sectors=['TEST', 'FOO']
        )
        company_user = models.CompanyUser.objects.create(company=company, **SUPPLIER_DATA)

        data = {
            'action': 'download_csv',
            '_selected_action': models.CompanyUser.objects.all().values_list('pk', flat=True)
        }
        response = self.client.post(
            reverse('admin:company_companyuser_changelist'),
            data,
            follow=True
        )

        expected_data = OrderedDict([
            ('company__address_line_1', 'test_address_line_1'),
            ('company__address_line_2', 'test_address_line_2'),
            ('company__companies_house_company_status', ''),
            ('company__country', 'test_country'),
            ('company__created', '2012-01-14 12:00:00+00:00'),
            ('company__date_identity_check_message_sent', ''),
            ('company__date_of_creation', '2010-10-10'),
            ('company__date_published', ''),
            ('company__date_registration_letter_sent', ''),
            ('company__date_verification_letter_sent', ''),
            ('company__description', 'Company description'),
            ('company__email_address', ''),
            ('company__email_full_name', ''),
            ('company__employees', ''),
            ('company__expertise_countries', "['GB']"),
            ('company__expertise_industries', "['INS']"),
            ('company__expertise_languages', "['ENG']"),
            ('company__expertise_products_services', '{}'),
            ('company__expertise_regions', "['UKG3']"),
            ('company__export_destinations', "['DE']"),
            ('company__export_destinations_other', 'LY'),
            ('company__facebook_url', ''),
            ('company__has_case_study', 'False'),
            ('company__has_exported_before', 'True'),
            ('company__id', str(company_user.company.pk)),
            ('company__is_exporting_goods', 'False'),
            ('company__is_exporting_services', 'False'),
            ('company__is_identity_check_message_sent', 'False'),
            ('company__is_published_find_a_supplier', 'False'),
            ('company__is_published_investment_support_directory', 'False'),
            ('company__is_registration_letter_sent', 'False'),
            ('company__is_showcase_company', 'False'),
            ('company__is_uk_isd_company', 'False'),
            ('company__is_verification_letter_sent', 'False'),
            ('company__keywords', ''),
            ('company__linkedin_url', ''),
            ('company__locality', 'test_locality'),
            ('company__logo', ''),
            ('company__mobile_number', '07505605132'),
            ('company__modified', '2012-01-14 12:00:00+00:00'),
            ('company__name', 'Test Company'),
            ('company__number', '11234567'),
            ('company__number_of_case_studies', '0'),
            ('company__number_of_sectors', '2'),
            ('company__po_box', ''),
            ('company__postal_code', 'test_postal_code'),
            ('company__postal_full_name', 'test_full_name'),
            ('company__sectors', '"TEST,FOO"'),
            ('company__slug', 'test-company'),
            ('company__summary', ''),
            ('company__twitter_url', ''),
            ('company__verified_with_code', 'False'),
            ('company__verified_with_companies_house_oauth2', 'False'),
            ('company__verified_with_identity_check', 'False'),
            ('company__verified_with_preverified_enrolment', 'False'),
            ('company__website', 'http://example.com'),
            ('company_email', 'gargoyle@example.com'),
            ('date_joined', '2017-03-21 13:12:00+00:00'),
            ('is_active', 'True'),
            ('mobile_number', ''),
            ('name', ''),
            ('role', 'EDITOR'),
            ('sso_id', '1'),
            ('unsubscribed', 'False'),
        ])

        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == ','.join(expected_data.keys())
        assert actual[1] == ','.join(expected_data.values())

    def test_download_csv_company_sectors_is_empty(self):
        company = models.Company.objects.create(
            **COMPANY_DATA,
            sectors=[]
        )
        company_user = models.CompanyUser.objects.create(company=company, **SUPPLIER_DATA)

        data = {
            'action': 'download_csv',
            '_selected_action': models.CompanyUser.objects.all().values_list('pk', flat=True)
        }
        response = self.client.post(
            reverse('admin:company_companyuser_changelist'),
            data,
            follow=True
        )

        expected_data = OrderedDict([
            ('company__address_line_1', 'test_address_line_1'),
            ('company__address_line_2', 'test_address_line_2'),
            ('company__companies_house_company_status', ''),
            ('company__country', 'test_country'),
            ('company__created', '2012-01-14 12:00:00+00:00'),
            ('company__date_identity_check_message_sent', ''),
            ('company__date_of_creation', '2010-10-10'),
            ('company__date_published', ''),
            ('company__date_registration_letter_sent', ''),
            ('company__date_verification_letter_sent', ''),
            ('company__description', 'Company description'),
            ('company__email_address', ''),
            ('company__email_full_name', ''),
            ('company__employees', ''),
            ('company__expertise_countries', "['GB']"),
            ('company__expertise_industries', "['INS']"),
            ('company__expertise_languages', "['ENG']"),
            ('company__expertise_products_services', '{}'),
            ('company__expertise_regions', "['UKG3']"),
            ('company__export_destinations', "['DE']"),
            ('company__export_destinations_other', 'LY'),
            ('company__facebook_url', ''),
            ('company__has_case_study', 'False'),
            ('company__has_exported_before', 'True'),
            ('company__id', str(company_user.company.pk)),
            ('company__is_exporting_goods', 'False'),
            ('company__is_exporting_services', 'False'),
            ('company__is_identity_check_message_sent', 'False'),
            ('company__is_published_find_a_supplier', 'False'),
            ('company__is_published_investment_support_directory', 'False'),
            ('company__is_registration_letter_sent', 'False'),
            ('company__is_showcase_company', 'False'),
            ('company__is_uk_isd_company', 'False'),
            ('company__is_verification_letter_sent', 'False'),
            ('company__keywords', ''),
            ('company__linkedin_url', ''),
            ('company__locality', 'test_locality'),
            ('company__logo', ''),
            ('company__mobile_number', '07505605132'),
            ('company__modified', '2012-01-14 12:00:00+00:00'),
            ('company__name', 'Test Company'),
            ('company__number', '11234567'),
            ('company__number_of_case_studies', '0'),
            ('company__number_of_sectors', '0'),
            ('company__po_box', ''),
            ('company__postal_code', 'test_postal_code'),
            ('company__postal_full_name', 'test_full_name'),
            ('company__sectors', ''),
            ('company__slug', 'test-company'),
            ('company__summary', ''),
            ('company__twitter_url', ''),
            ('company__verified_with_code', 'False'),
            ('company__verified_with_companies_house_oauth2', 'False'),
            ('company__verified_with_identity_check', 'False'),
            ('company__verified_with_preverified_enrolment', 'False'),
            ('company__website', 'http://example.com'),
            ('company_email', 'gargoyle@example.com'),
            ('date_joined', '2017-03-21 13:12:00+00:00'),
            ('is_active', 'True'),
            ('mobile_number', ''),
            ('name', ''),
            ('role', 'EDITOR'),
            ('sso_id', '1'),
            ('unsubscribed', 'False'),
        ])
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0].split(',') == list(expected_data.keys())
        assert actual[1].split(',') == list(expected_data.values())

    def test_download_csv_multiple_suppliers(self):
        company_data2 = COMPANY_DATA.copy()
        company_data2['number'] = '01234568'
        supplier_data2 = SUPPLIER_DATA.copy()
        supplier_data2.update({
            'sso_id': 2,
            'company_email': '2@example.com',
        })
        company1 = models.Company.objects.create(**COMPANY_DATA)
        company2 = models.Company.objects.create(**company_data2)
        models.CompanyCaseStudy.objects.create(
            title='foo',
            description='bar',
            company=company1
        )
        models.CompanyUser.objects.create(company=company1, **SUPPLIER_DATA)
        models.CompanyUser.objects.create(company=company2, **supplier_data2)

        supplier_one_expected = OrderedDict([
            ('company__address_line_1', 'test_address_line_1'),
            ('company__address_line_2', 'test_address_line_2'),
            ('company__companies_house_company_status', ''),
            ('company__country', 'test_country'),
            ('company__created', '2012-01-14 12:00:00+00:00'),
            ('company__date_identity_check_message_sent', ''),
            ('company__date_of_creation', '2010-10-10'),
            ('company__date_published', ''),
            ('company__date_registration_letter_sent', ''),
            ('company__date_verification_letter_sent', ''),
            ('company__description', 'Company description'),
            ('company__email_address', ''),
            ('company__email_full_name', ''),
            ('company__employees', ''),
            ('company__expertise_countries', "['GB']"),
            ('company__expertise_industries', "['INS']"),
            ('company__expertise_languages', "['ENG']"),
            ('company__expertise_products_services', '{}'),
            ('company__expertise_regions', "['UKG3']"),
            ('company__export_destinations', "['DE']"),
            ('company__export_destinations_other', 'LY'),
            ('company__facebook_url', ''),
            ('company__has_case_study', 'True'),
            ('company__has_exported_before', 'True'),
            ('company__id', str(company1.pk)),
            ('company__is_exporting_goods', 'False'),
            ('company__is_exporting_services', 'False'),
            ('company__is_identity_check_message_sent', 'False'),
            ('company__is_published_find_a_supplier', 'False'),
            ('company__is_published_investment_support_directory', 'False'),
            ('company__is_registration_letter_sent', 'False'),
            ('company__is_showcase_company', 'False'),
            ('company__is_uk_isd_company', 'False'),
            ('company__is_verification_letter_sent', 'False'),
            ('company__keywords', ''),
            ('company__linkedin_url', ''),
            ('company__locality', 'test_locality'),
            ('company__logo', ''),
            ('company__mobile_number', '07505605132'),
            ('company__modified', '2012-01-14 12:00:00+00:00'),
            ('company__name', 'Test Company'),
            ('company__number', '11234567'),
            ('company__number_of_case_studies', '1'),
            ('company__number_of_sectors', '0'),
            ('company__po_box', ''),
            ('company__postal_code', 'test_postal_code'),
            ('company__postal_full_name', 'test_full_name'),
            ('company__sectors', ''),
            ('company__slug', 'test-company'),
            ('company__summary', ''),
            ('company__twitter_url', ''),
            ('company__verified_with_code', 'False'),
            ('company__verified_with_companies_house_oauth2', 'False'),
            ('company__verified_with_identity_check', 'False'),
            ('company__verified_with_preverified_enrolment', 'False'),
            ('company__website', 'http://example.com'),
            ('company_email', 'gargoyle@example.com'),
            ('date_joined', '2017-03-21 13:12:00+00:00'),
            ('is_active', 'True'),
            ('mobile_number', ''),
            ('name', ''),
            ('role', 'EDITOR'),
            ('sso_id', '1'),
            ('unsubscribed', 'False'),
        ])

        supplier_two_expected = OrderedDict([
            ('company__address_line_1', 'test_address_line_1'),
            ('company__address_line_2', 'test_address_line_2'),
            ('company__companies_house_company_status', ''),
            ('company__country', 'test_country'),
            ('company__created', '2012-01-14 12:00:00+00:00'),
            ('company__date_identity_check_message_sent', ''),
            ('company__date_of_creation', '2010-10-10'),
            ('company__date_published', ''),
            ('company__date_registration_letter_sent', ''),
            ('company__date_verification_letter_sent', ''),
            ('company__description', 'Company description'),
            ('company__email_address', ''),
            ('company__email_full_name', ''),
            ('company__employees', ''),
            ('company__expertise_countries', "['GB']"),
            ('company__expertise_industries', "['INS']"),
            ('company__expertise_languages', "['ENG']"),
            ('company__expertise_products_services', '{}'),
            ('company__expertise_regions', "['UKG3']"),
            ('company__export_destinations', "['DE']"),
            ('company__export_destinations_other', 'LY'),
            ('company__facebook_url', ''),
            ('company__has_case_study', 'False'),
            ('company__has_exported_before', 'True'),
            ('company__id', str(company2.pk)),
            ('company__is_exporting_goods', 'False'),
            ('company__is_exporting_services', 'False'),
            ('company__is_identity_check_message_sent', 'False'),
            ('company__is_published_find_a_supplier', 'False'),
            ('company__is_published_investment_support_directory', 'False'),
            ('company__is_registration_letter_sent', 'False'),
            ('company__is_showcase_company', 'False'),
            ('company__is_uk_isd_company', 'False'),
            ('company__is_verification_letter_sent', 'False'),
            ('company__keywords', ''),
            ('company__linkedin_url', ''),
            ('company__locality', 'test_locality'),
            ('company__logo', ''),
            ('company__mobile_number', '07505605132'),
            ('company__modified', '2012-01-14 12:00:00+00:00'),
            ('company__name', 'Test Company'),
            ('company__number', '01234568'),
            ('company__number_of_case_studies', '0'),
            ('company__number_of_sectors', '0'),
            ('company__po_box', ''),
            ('company__postal_code', 'test_postal_code'),
            ('company__postal_full_name', 'test_full_name'),
            ('company__sectors', ''),
            ('company__slug', 'test-company'),
            ('company__summary', ''),
            ('company__twitter_url', ''),
            ('company__verified_with_code', 'False'),
            ('company__verified_with_companies_house_oauth2', 'False'),
            ('company__verified_with_identity_check', 'False'),
            ('company__verified_with_preverified_enrolment', 'False'),
            ('company__website', 'http://example.com'),
            ('company_email', '2@example.com'),
            ('date_joined', '2017-03-21 13:12:00+00:00'),
            ('is_active', 'True'),
            ('mobile_number', ''),
            ('name', ''),
            ('role', 'EDITOR'),
            ('sso_id', '2'),
            ('unsubscribed', 'False'),

        ])
        data = {
            'action': 'download_csv',
            '_selected_action': models.CompanyUser.objects.all().values_list('pk', flat=True)
        }
        response = self.client.post(
            reverse('admin:company_companyuser_changelist'),
            data,
            follow=True
        )
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0].split(',') == list(supplier_one_expected.keys())
        assert actual[1].split(',') == list(supplier_two_expected.values())
        assert actual[2].split(',') == list(supplier_one_expected.values())


@pytest.mark.django_db
class ResendLetterTestCase(TestCase):

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

    @patch('company.admin.messages')
    @patch('company.helpers.send_verification_letter')
    def test_resend_letter(self, mocked_send_letter, mocked_messages):
        company = models.Company.objects.create(**COMPANY_DATA)
        company_user = models.CompanyUser.objects.create(company=company, **SUPPLIER_DATA)

        # already verified company_user
        other_company_data = COMPANY_DATA.copy()
        other_supplier_data = SUPPLIER_DATA.copy()
        other_company_data['number'] = '12345678'
        other_company_data['verified_with_code'] = True
        other_supplier_data['sso_id'] = 2
        other_supplier_data['company_email'] = 'test@foo.com'
        other_company = models.Company.objects.create(**other_company_data)
        models.CompanyUser.objects.create(company=other_company, **other_supplier_data)

        data = {
            'action': 'resend_letter',
            '_selected_action': models.CompanyUser.objects.all().values_list('pk', flat=True)
        }
        response = self.client.post(
            reverse('admin:company_companyuser_changelist'),
            data,
            follow=True
        )

        assert mocked_send_letter.called_once_with(company_user.company)
        assert mocked_messages.success.called_once_with(
            response.request,
            'Verification letter resent to 1 users'
        )
        assert mocked_messages.warning.called_once_with(
            response.request,
            '1 users skipped'
        )
