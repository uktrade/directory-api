import http
from unittest import mock

import pytest

from rest_framework.test import APIClient

from django.core.urlresolvers import reverse

from enrolment import helpers, models, views
from enrolment.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
@mock.patch('boto3.resource')
def test_enrolment_viewset_create(boto_mock):
    client = APIClient()
    response = client.post(
        '/enrolment/', VALID_REQUEST_DATA, format='json'
    )

    assert response.status_code == http.client.ACCEPTED
    assert not models.Enrolment.objects.all().exists()


@mock.patch.object(helpers, 'send_verification_code_via_sms',
                   return_value='123')
def test_send_sms_good_serializer(mock_send_verification_code_via_sms, rf):
    request = rf.post(reverse('verification-sms'), {'phone_number': '0123'})

    response = views.SendSMSVerificationAPIView.as_view()(request)

    assert response.status_code == http.client.OK


def test_send_sms_bad_serializer(rf):
    request = rf.post(reverse('verification-sms'), {})

    response = views.SendSMSVerificationAPIView.as_view()(request)

    assert response.status_code == http.client.BAD_REQUEST


@mock.patch.object(helpers, 'send_verification_code_via_sms',
                   return_value='123')
def test_send_sms_calls_helper(mock_send_verification_code_via_sms, rf):
    request = rf.post(reverse('verification-sms'), {'phone_number': '0123'})

    response = views.SendSMSVerificationAPIView.as_view()(request)

    mock_send_verification_code_via_sms.assert_called_once_with(
        phone_number='0123',
    )
    assert response.data == {'sms_code': '123'}
