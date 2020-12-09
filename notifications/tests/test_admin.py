from collections import OrderedDict
from unittest import TestCase

import pytest
from django.contrib.auth.models import User
from django.test import Client
from django.urls import reverse

from notifications.models import AnonymousEmailNotification, SupplierEmailNotification
from notifications.tests.factories import AnonymousEmailNotificationFactory, SupplierEmailNotificationFactory


@pytest.mark.django_db
class DownloadCSVTestCase(TestCase):
    def setUp(self):
        superuser = User.objects.create_superuser(username='admin', email='admin@example.com', password='test')
        self.client = Client()
        self.client.force_login(superuser)

    def test_download_csv_supplier_email_notification(self):
        supplier_email_notification = SupplierEmailNotificationFactory()

        data = {
            'action': 'download_csv',
            '_selected_action': SupplierEmailNotification.objects.all().values_list('pk', flat=True),
        }
        response = self.client.post(
            reverse('admin:notifications_supplieremailnotification_changelist'), data, follow=True
        )

        expected_data = OrderedDict(
            [
                ('category', str(supplier_email_notification.category)),
                ('company_user', str(supplier_email_notification.company_user.id)),
                ('date_sent', str(supplier_email_notification.date_sent)),
                ('id', str(supplier_email_notification.id)),
            ]
        )
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == ','.join(expected_data.keys())
        assert actual[1] == ','.join(expected_data.values())

    def test_download_csv_supplier_email_notification_no_company(self):
        SupplierEmailNotificationFactory(company_user__company=None)

        response = self.client.get(reverse('admin:notifications_supplieremailnotification_changelist'))

        assert response.status_code == 200

    def test_download_csv_multiple_supplier_email_notifications(self):
        supplier_email_notifications = SupplierEmailNotificationFactory.create_batch(3)

        supplier_email_notification_one_expected_data = OrderedDict(
            [
                ('category', str(supplier_email_notifications[2].category)),
                ('company_user', str(supplier_email_notifications[2].company_user.id)),
                ('date_sent', str(supplier_email_notifications[2].date_sent)),
                ('id', str(supplier_email_notifications[2].id)),
            ]
        )
        supplier_email_notification_two_expected_data = OrderedDict(
            [
                ('category', str(supplier_email_notifications[1].category)),
                ('company_user', str(supplier_email_notifications[1].company_user.id)),
                ('date_sent', str(supplier_email_notifications[1].date_sent)),
                ('id', str(supplier_email_notifications[1].id)),
            ]
        )
        supplier_email_notification_three_expected_data = OrderedDict(
            [
                ('category', str(supplier_email_notifications[0].category)),
                ('company_user', str(supplier_email_notifications[0].company_user.id)),
                ('date_sent', str(supplier_email_notifications[0].date_sent)),
                ('id', str(supplier_email_notifications[0].id)),
            ]
        )

        data = {
            'action': 'download_csv',
            '_selected_action': SupplierEmailNotification.objects.all().values_list('pk', flat=True),
        }
        response = self.client.post(
            reverse('admin:notifications_supplieremailnotification_changelist'), data, follow=True
        )

        actual = str(response.content, 'utf-8').split('\r\n')
        assert actual[0] == ','.join(supplier_email_notification_one_expected_data.keys())
        assert actual[1] == ','.join(supplier_email_notification_one_expected_data.values())
        assert actual[2] == ','.join(supplier_email_notification_two_expected_data.values())
        assert actual[3] == ','.join(supplier_email_notification_three_expected_data.values())

    def test_download_csv_anonymous_email_notification(self):
        anonymous_email_notification = AnonymousEmailNotificationFactory()

        data = {
            'action': 'download_csv',
            '_selected_action': AnonymousEmailNotification.objects.all().values_list('pk', flat=True),
        }
        response = self.client.post(
            reverse('admin:notifications_anonymousemailnotification_changelist'), data, follow=True
        )

        expected_data = OrderedDict(
            [
                ('category', str(anonymous_email_notification.category)),
                ('date_sent', str(anonymous_email_notification.date_sent)),
                ('email', str(anonymous_email_notification.email)),
                ('id', str(anonymous_email_notification.id)),
            ]
        )
        actual = str(response.content, 'utf-8').split('\r\n')

        assert actual[0] == ','.join(expected_data.keys())
        assert actual[1] == ','.join(expected_data.values())

    def test_download_csv_multiple_anonymous_email_notifications(self):
        anonymous_email_notifications = AnonymousEmailNotificationFactory.create_batch(3)

        anonymous_email_notification_one_expected_data = OrderedDict(
            [
                ('category', str(anonymous_email_notifications[2].category)),
                ('date_sent', str(anonymous_email_notifications[2].date_sent)),
                ('email', str(anonymous_email_notifications[2].email)),
                ('id', str(anonymous_email_notifications[2].id)),
            ]
        )
        anonymous_email_notification_two_expected_data = OrderedDict(
            [
                ('category', str(anonymous_email_notifications[1].category)),
                ('date_sent', str(anonymous_email_notifications[1].date_sent)),
                ('email', str(anonymous_email_notifications[1].email)),
                ('id', str(anonymous_email_notifications[1].id)),
            ]
        )
        anonymous_email_notification_three_expected_data = OrderedDict(
            [
                ('category', str(anonymous_email_notifications[0].category)),
                ('date_sent', str(anonymous_email_notifications[0].date_sent)),
                ('email', str(anonymous_email_notifications[0].email)),
                ('id', str(anonymous_email_notifications[0].id)),
            ]
        )

        data = {
            'action': 'download_csv',
            '_selected_action': AnonymousEmailNotification.objects.all().values_list('pk', flat=True),
        }
        response = self.client.post(
            reverse('admin:notifications_anonymousemailnotification_changelist'), data, follow=True
        )

        actual = str(response.content, 'utf-8').split('\r\n')
        assert actual[0] == ','.join(anonymous_email_notification_one_expected_data.keys())
        assert actual[1] == ','.join(anonymous_email_notification_one_expected_data.values())
        assert actual[2] == ','.join(anonymous_email_notification_two_expected_data.values())
        assert actual[3] == ','.join(anonymous_email_notification_three_expected_data.values())
