from collections import OrderedDict
from unittest import TestCase

from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

import pytest

from exportreadiness.models import TriageResult
from .factories import TriageResultFactory


@pytest.mark.django_db
class TriageResultDownloadCSVTestCase(TestCase):

    def setUp(self):
        superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='test'
        )
        self.client = Client()
        self.client.force_login(superuser)

    def test_download_csv(self):
        triage_result = TriageResultFactory(sso_id=1)

        data = {
            'action': 'download_csv',
            '_selected_action': TriageResult.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:exportreadiness_triageresult_changelist'),
            data,
            follow=True
        )

        expected_data = OrderedDict([
            ('company_name', str(triage_result.company_name)),
            ('company_number', ''),
            ('created', str(triage_result.created)),
            ('exported_before', str(triage_result.exported_before)),
            ('id', str(triage_result.id)),
            (
                'is_in_companies_house',
                str(triage_result.is_in_companies_house)
            ),
            ('modified', str(triage_result.modified)),
            ('regular_exporter', str(triage_result.regular_exporter)),
            ('sector', triage_result.sector),
            ('sso_id', str(triage_result.sso_id)),
            (
                'used_online_marketplace',
                str(triage_result.used_online_marketplace)
            )
        ])
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == ','.join(expected_data.keys())
        assert actual[1] == ','.join(expected_data.values())

    def test_download_csv_multiple_buyers(self):
        triage_result_one = TriageResultFactory(sso_id=1)
        triage_result_two = TriageResultFactory(sso_id=2, company_number=2)
        triage_result_three = TriageResultFactory(sso_id=3, company_number=1)

        data = {
            'action': 'download_csv',
            '_selected_action': TriageResult.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:exportreadiness_triageresult_changelist'),
            data,
            follow=True
        )

        triage_result_one_expected_data = OrderedDict([
            ('company_name', str(triage_result_one.company_name)),
            ('company_number', ''),
            ('created', str(triage_result_one.created)),
            ('exported_before', str(triage_result_one.exported_before)),
            ('id', str(triage_result_one.id)),
            (
                'is_in_companies_house',
                str(triage_result_one.is_in_companies_house)
            ),
            ('modified', str(triage_result_one.modified)),
            ('regular_exporter', str(triage_result_one.regular_exporter)),
            ('sector', triage_result_one.sector),
            ('sso_id', str(triage_result_one.sso_id)),
            (
                'used_online_marketplace',
                str(triage_result_one.used_online_marketplace)
            )
        ])
        triage_result_two_expected_data = OrderedDict([
            ('company_name', str(triage_result_two.company_name)),
            ('company_number', str(triage_result_two.company_number)),
            ('created', str(triage_result_two.created)),
            ('exported_before', str(triage_result_two.exported_before)),
            ('id', str(triage_result_two.id)),
            (
                'is_in_companies_house',
                str(triage_result_two.is_in_companies_house)
            ),
            ('modified', str(triage_result_two.modified)),
            ('regular_exporter', str(triage_result_two.regular_exporter)),
            ('sector', triage_result_two.sector),
            ('sso_id', str(triage_result_two.sso_id)),
            (
                'used_online_marketplace',
                str(triage_result_two.used_online_marketplace)
            )
        ])
        triage_result_three_expected_data = OrderedDict([
            ('company_name', str(triage_result_three.company_name)),
            ('company_number', str(triage_result_three.company_number)),
            ('created', str(triage_result_three.created)),
            ('exported_before', str(triage_result_three.exported_before)),
            ('id', str(triage_result_three.id)),
            (
                'is_in_companies_house',
                str(triage_result_three.is_in_companies_house)
            ),
            ('modified', str(triage_result_three.modified)),
            ('regular_exporter', str(triage_result_three.regular_exporter)),
            ('sector', triage_result_three.sector),
            ('sso_id', str(triage_result_three.sso_id)),
            (
                'used_online_marketplace',
                str(triage_result_three.used_online_marketplace)
            )
        ])
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == ','.join(triage_result_one_expected_data.keys())
        assert actual[1] == ','.join(
            triage_result_three_expected_data.values()
        )
        assert actual[2] == ','.join(triage_result_two_expected_data.values())
        assert actual[3] == ','.join(triage_result_one_expected_data.values())
