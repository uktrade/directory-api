import http
from unittest.mock import Mock, patch

import pytest
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status

from buyer import models
from core.tests.test_views import reload_module, reload_urlconf


@pytest.mark.django_db
@patch('sigauth.helpers.RequestSignatureChecker.test_signature', Mock(return_value=True))
def test_create_buyer_deserialization(client):
    data = {
        'email': 'jim@example.com',
        'name': 'Jim Exampleson',
        'sector': 'AEROSPACE',
        'company_name': 'Example corp',
        'country': 'China',
        'comment': 'Good stuff.',
    }
    response = client.post(reverse('buyer-create'), data)
    instance = models.Buyer.objects.last()

    assert response.status_code == http.client.CREATED
    assert instance.email == data['email']
    assert instance.name == data['name']
    assert instance.sector == data['sector']


@pytest.mark.django_db
@patch('sigauth.helpers.RequestSignatureChecker.test_signature', Mock(return_value=True))
@patch('core.views.get_file_from_s3')
@override_settings(STORAGE_CLASS_NAME='default')
@override_settings(AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE='my_db_buket')
def test_buyer_csv_dump(mocked_get_file_from_s3, authed_client):
    reload_module('company.views')
    reload_module('buyer.views')
    reload_urlconf()
    mocked_body = Mock()
    mocked_body.read.return_value = b'company_name\r\nacme\r\n'
    mocked_get_file_from_s3.return_value = {'Body': mocked_body}
    response = authed_client.get(reverse('buyer-csv-dump'), {'token': settings.CSV_DUMP_AUTH_TOKEN})
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b'company_name\r\nacme\r\n'
    assert response.headers['content-type'] == 'text/csv'
    assert response.headers['content-disposition'] == f'attachment; filename="{settings.BUYERS_CSV_FILE_NAME}"'
