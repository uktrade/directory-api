from collections import OrderedDict
from unittest import TestCase

from django.test import Client
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

import pytest

from buyer.models import Buyer
from buyer.tests.factories import BuyerFactory


@pytest.mark.django_db
class DownloadCSVTestCase(TestCase):

    def setUp(self):
        superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='test'
        )
        self.client = Client()
        self.client.force_login(superuser)

    def test_download_csv(self):
        buyer = BuyerFactory()

        data = {
            'action': 'download_csv',
            '_selected_action': Buyer.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:buyer_buyer_changelist'),
            data,
            follow=True
        )

        expected_data = OrderedDict([
            ('created', str(buyer.created)),
            ('email', buyer.email),
            ('id', str(buyer.id)),
            ('modified', str(buyer.modified)),
            ('name', buyer.name),
            ('sector', buyer.sector),
        ])
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == ','.join(expected_data.keys())
        assert actual[1] == ','.join(expected_data.values())

    def test_download_csv_multiple_buyers(self):
        buyers = BuyerFactory.create_batch(3)
        buyer_one_expected_data = OrderedDict([
            ('created', str(buyers[0].created)),
            ('email', buyers[0].email),
            ('id', str(buyers[0].id)),
            ('modified', str(buyers[0].modified)),
            ('name', buyers[0].name),
            ('sector', buyers[0].sector),
        ])
        buyer_two_expected_data = OrderedDict([
            ('created', str(buyers[1].created)),
            ('email', buyers[1].email),
            ('id', str(buyers[1].id)),
            ('modified', str(buyers[1].modified)),
            ('name', buyers[1].name),
            ('sector', buyers[1].sector),
        ])
        buyer_three_expected_data = OrderedDict([
            ('created', str(buyers[2].created)),
            ('email', buyers[2].email),
            ('id', str(buyers[2].id)),
            ('modified', str(buyers[2].modified)),
            ('name', buyers[2].name),
            ('sector', buyers[2].sector),
        ])

        data = {
            'action': 'download_csv',
            '_selected_action': Buyer.objects.all().values_list(
                'pk', flat=True
            )
        }
        response = self.client.post(
            reverse('admin:buyer_buyer_changelist'),
            data,
            follow=True
        )

        actual = str(response.content, 'utf-8').split('\r\n')
        assert actual[0] == ','.join(buyer_one_expected_data.keys())
        assert actual[1] == ','.join(buyer_three_expected_data.values())
        assert actual[2] == ','.join(buyer_two_expected_data.values())
        assert actual[3] == ','.join(buyer_one_expected_data.values())
