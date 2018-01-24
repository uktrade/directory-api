import http
from unittest.mock import patch, Mock

import pytest
from django.conf import settings

from django.core.urlresolvers import reverse
from rest_framework import status

from buyer import models


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission',
       Mock(return_value=True))
def test_create_buyer_deserialization(authed_client):
    data = {
        'email': 'jim@example.com',
        'name': 'Jim Exampleson',
        'sector': 'AEROSPACE',
        'company_name': 'Example corp',
        'country': 'China',
        'comment': 'Good stuff.',
    }
    response = authed_client.post(reverse('buyer-create'), data)
    instance = models.Buyer.objects.last()

    assert response.status_code == http.client.CREATED
    assert instance.email == data['email']
    assert instance.name == data['name']
    assert instance.sector == data['sector']


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission',
       Mock(return_value=True))
@patch('core.views.get_file_from_s3')
def test_buyer_csv_dump(mocked_get_file_from_s3, authed_client):
    mocked_body = Mock()
    mocked_body.read.return_value = b'company_name\r\nacme\r\n'
    mocked_get_file_from_s3.return_value = {
        'Body': mocked_body
    }
    response = authed_client.get(
        reverse('buyer-csv-dump'),
        {'token': settings.CSV_DUMP_AUTH_TOKEN}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b'company_name\r\nacme\r\n'
    assert response._headers['content-type'] == ('Content-Type', 'text/csv')
    assert response._headers['content-disposition'] == (
        'Content-Disposition',
        'attachment; filename="{filename}"'.format(
            filename=settings.BUYERS_CSV_FILE_NAME
        )
    )
