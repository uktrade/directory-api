from collections import OrderedDict
from unittest import TestCase
from unittest.mock import patch

from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

import pytest

from freezegun import freeze_time

from supplier.models import Supplier
from supplier.tests import VALID_REQUEST_DATA as SUPPLIER_DATA
from company.models import Company, CompanyCaseStudy
from company.tests import VALID_REQUEST_DATA


COMPANY_DATA = VALID_REQUEST_DATA.copy()


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
        company = Company.objects.create(
            **COMPANY_DATA,
            sectors=['TEST', 'FOO']
        )
        supplier = Supplier.objects.create(company=company, **SUPPLIER_DATA)

        data = {
            'action': 'download_csv',
            '_selected_action': Supplier.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:supplier_supplier_changelist'),
            data,
            follow=True
        )

        expected_data = OrderedDict([
            ('company__address_line_1', 'test_address_line_1'),
            ('company__address_line_2', 'test_address_line_2'),
            ('company__country', 'test_country'),
            ('company__created', '2012-01-14 12:00:00+00:00'),
            ('company__date_of_creation', '2010-10-10'),
            ('company__date_published', ''),
            ('company__date_verification_letter_sent', ''),
            ('company__description', 'Company description'),
            ('company__email_address', ''),
            ('company__email_full_name', ''),
            ('company__employees', ''),
            ('company__export_destinations', "['DE']"),
            ('company__export_destinations_other', 'LY'),
            ('company__facebook_url', ''),
            ('company__has_case_study', 'False'),
            ('company__has_exported_before', 'True'),
            ('company__id', str(supplier.company.pk)),
            ('company__is_exporting_goods', 'False'),
            ('company__is_exporting_services', 'False'),
            ('company__is_published', 'False'),
            ('company__is_showcase_company', 'False'),
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
            ('company__verified_with_preverified_enrolment', 'False'),
            ('company__website', 'http://example.com'),
            ('company_email', 'gargoyle@example.com'),
            ('date_joined', '2017-03-21 13:12:00+00:00'),
            ('is_active', 'True'),
            ('is_company_owner', 'False'),
            ('mobile_number', ''),
            ('name', ''),
            ('sso_id', '1'),
            ('unsubscribed', 'False'),
        ])
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == ','.join(expected_data.keys())
        assert actual[1] == ','.join(expected_data.values())

    def test_download_csv_company__sectors_is_empty(self):
        company = Company.objects.create(
            **COMPANY_DATA,
            sectors=[]
        )
        supplier = Supplier.objects.create(company=company, **SUPPLIER_DATA)

        data = {
            'action': 'download_csv',
            '_selected_action': Supplier.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:supplier_supplier_changelist'),
            data,
            follow=True
        )

        expected_data = OrderedDict([
            ('company__address_line_1', 'test_address_line_1'),
            ('company__address_line_2', 'test_address_line_2'),
            ('company__country', 'test_country'),
            ('company__created', '2012-01-14 12:00:00+00:00'),
            ('company__date_of_creation', '2010-10-10'),
            ('company__date_published', ''),
            ('company__date_verification_letter_sent', ''),
            ('company__description', 'Company description'),
            ('company__email_address', ''),
            ('company__email_full_name', ''),
            ('company__employees', ''),
            ('company__export_destinations', "['DE']"),
            ('company__export_destinations_other', 'LY'),
            ('company__facebook_url', ''),
            ('company__has_case_study', 'False'),
            ('company__has_exported_before', 'True'),
            ('company__id', str(supplier.company.pk)),
            ('company__is_exporting_goods', 'False'),
            ('company__is_exporting_services', 'False'),
            ('company__is_published', 'False'),
            ('company__is_showcase_company', 'False'),
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
            ('company__verified_with_preverified_enrolment', 'False'),
            ('company__website', 'http://example.com'),
            ('company_email', 'gargoyle@example.com'),
            ('date_joined', '2017-03-21 13:12:00+00:00'),
            ('is_active', 'True'),
            ('is_company_owner', 'False'),
            ('mobile_number', ''),
            ('name', ''),
            ('sso_id', '1'),
            ('unsubscribed', 'False'),
        ])
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == ','.join(expected_data.keys())
        assert actual[1] == ','.join(expected_data.values())

    def test_download_csv_multiple_suppliers(self):
        company_data2 = COMPANY_DATA.copy()
        company_data2['number'] = '01234568'
        supplier_data2 = SUPPLIER_DATA.copy()
        supplier_data2.update({
            'sso_id': 2,
            'company_email': '2@example.com',
        })
        company1 = Company.objects.create(**COMPANY_DATA)
        company2 = Company.objects.create(**company_data2)
        CompanyCaseStudy.objects.create(
            title='foo',
            description='bar',
            company=company1
        )
        Supplier.objects.create(company=company1, **SUPPLIER_DATA)
        Supplier.objects.create(company=company2, **supplier_data2)

        supplier_one_expected_data = OrderedDict([
            ('company__address_line_1', 'test_address_line_1'),
            ('company__address_line_2', 'test_address_line_2'),
            ('company__country', 'test_country'),
            ('company__created', '2012-01-14 12:00:00+00:00'),
            ('company__date_of_creation', '2010-10-10'),
            ('company__date_published', ''),
            ('company__date_verification_letter_sent', ''),
            ('company__description', 'Company description'),
            ('company__email_address', ''),
            ('company__email_full_name', ''),
            ('company__employees', ''),
            ('company__export_destinations', "['DE']"),
            ('company__export_destinations_other', 'LY'),
            ('company__facebook_url', ''),
            ('company__has_case_study', 'True'),
            ('company__has_exported_before', 'True'),
            ('company__id', str(company1.pk)),
            ('company__is_exporting_goods', 'False'),
            ('company__is_exporting_services', 'False'),
            ('company__is_published', 'False'),
            ('company__is_showcase_company', 'False'),
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
            ('company__verified_with_preverified_enrolment', 'False'),
            ('company__website', 'http://example.com'),
            ('company_email', 'gargoyle@example.com'),
            ('date_joined', '2017-03-21 13:12:00+00:00'),
            ('is_active', 'True'),
            ('is_company_owner', 'False'),
            ('mobile_number', ''),
            ('name', ''),
            ('sso_id', '1'),
            ('unsubscribed', 'False'),
        ])

        supplier_two_expected_data = OrderedDict([
            ('company__address_line_1', 'test_address_line_1'),
            ('company__address_line_2', 'test_address_line_2'),
            ('company__country', 'test_country'),
            ('company__created', '2012-01-14 12:00:00+00:00'),
            ('company__date_of_creation', '2010-10-10'),
            ('company__date_published', ''),
            ('company__date_verification_letter_sent', ''),
            ('company__description', 'Company description'),
            ('company__email_address', ''),
            ('company__email_full_name', ''),
            ('company__employees', ''),
            ('company__export_destinations', "['DE']"),
            ('company__export_destinations_other', 'LY'),
            ('company__facebook_url', ''),
            ('company__has_case_study', 'False'),
            ('company__has_exported_before', 'True'),
            ('company__id', str(company2.pk)),
            ('company__is_exporting_goods', 'False'),
            ('company__is_exporting_services', 'False'),
            ('company__is_published', 'False'),
            ('company__company__is_showcase_company', 'False'),
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
            ('company__verified_with_preverified_enrolment', 'False'),
            ('company__website', 'http://example.com'),
            ('company_email', '2@example.com'),
            ('date_joined', '2017-03-21 13:12:00+00:00'),
            ('is_active', 'True'),
            ('is_company_owner', 'False'),
            ('mobile_number', ''),
            ('name', ''),
            ('sso_id', '2'),
            ('unsubscribed', 'False'),
        ])
        data = {
            'action': 'download_csv',
            '_selected_action': Supplier.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:supplier_supplier_changelist'),
            data,
            follow=True
        )
        actual = str(response.content, 'utf-8').split('\r\n')
        assert actual[0] == ','.join(supplier_one_expected_data.keys())
        assert actual[1] == ','.join(supplier_two_expected_data.values())
        assert actual[2] == ','.join(supplier_one_expected_data.values())


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

    @patch('supplier.admin.messages')
    @patch('supplier.admin.send_verification_letter')
    def test_resend_letter(self, mocked_send_letter, mocked_messages):
        company = Company.objects.create(**COMPANY_DATA)
        supplier = Supplier.objects.create(company=company, **SUPPLIER_DATA)

        # already verified supplier
        other_company_data = COMPANY_DATA.copy()
        other_supplier_data = SUPPLIER_DATA.copy()
        other_company_data['number'] = '12345678'
        other_company_data['verified_with_code'] = True
        other_supplier_data['sso_id'] = 2
        other_supplier_data['company_email'] = 'test@foo.com'
        other_company = Company.objects.create(**other_company_data)
        Supplier.objects.create(company=other_company, **other_supplier_data)

        data = {
            'action': 'resend_letter',
            '_selected_action': Supplier.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:supplier_supplier_changelist'),
            data,
            follow=True
        )

        assert mocked_send_letter.called_once_with(supplier.company)
        assert mocked_messages.success.called_once_with(
            response.request,
            'Verification letter resent to 1 users'
        )
        assert mocked_messages.warning.called_once_with(
            response.request,
            '1 users skipped'
        )
