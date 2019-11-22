from collections import OrderedDict
from unittest import TestCase

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

import pytest

from freezegun import freeze_time

from company.models import Company
from contact.models import MessageToSupplier
from company.tests import VALID_REQUEST_DATA


COMPANY_DATA = VALID_REQUEST_DATA.copy()


@pytest.mark.django_db
class DownloadMessageToSupplierCSVTestCase(TestCase):

    def setUp(self):
        superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='test'
        )
        self.client = Client()
        self.client.force_login(superuser)

        self.freezer = freeze_time('2012-01-14 12:00:00')
        self.freezer.start()

    def tearDown(self):
        self.freezer.stop()

    def test_download_csv(self):
        recipient = Company.objects.create(**COMPANY_DATA)
        MessageToSupplier.objects.create(**dict(
            sender_email='foo@bar.com',
            sender_name='Testo Useri',
            sender_company_name='Acme',
            sender_country='Antartica',
            recipient=recipient
        ))

        data = {
            'action': 'download_csv',
            '_selected_action': MessageToSupplier.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:contact_messagetosupplier_changelist'),
            data,
            follow=True
        )

        expected_data = OrderedDict([
            ('created', '2012-01-14 12:00:00+00:00'),
            ('recipient__address_line_1', 'test_address_line_1'),
            ('recipient__address_line_2', 'test_address_line_2'),
            ('recipient__date_of_creation', '2010-10-10'),
            ('recipient__email_address', ''),
            ('recipient__name', 'Test Company'),
            ('recipient__number', '11234567'),
            ('recipient__postal_code', 'test_postal_code'),
            ('recipient__postal_full_name', 'test_full_name'),
            ('sender_company_name', 'Acme'),
            ('sender_country', 'Antartica'),
            ('sender_email', 'foo@bar.com'),
            ('sender_name', 'Testo Useri'),
        ])
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == ','.join(expected_data.keys())
        assert actual[1] == ','.join(expected_data.values())
