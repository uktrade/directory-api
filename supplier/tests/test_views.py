import base64
from unittest.mock import call, patch, Mock

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from django.conf import settings
from django.core.urlresolvers import reverse
from core.tests.test_views import reload_urlconf, reload_module

from supplier import helpers, models, serializers
from supplier.tests import factories, VALID_REQUEST_DATA
from directory_constants import user_roles


@pytest.fixture
def supplier():
    return factories.SupplierFactory(
        company_email='jim@example.com',
        company__number='01234567',
        company__name='foo ltd',
        company__sectors=['AEROSPACE'],
        name='Jim Example',
        sso_id=123,
        company__export_status='YES',
        company__has_exported_before=True,
    )


@pytest.mark.django_db
def test_supplier_retrieve(authed_client, authed_supplier):
    response = authed_client.get(reverse('supplier'))

    expected = serializers.SupplierSerializer(authed_supplier).data

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
def test_supplier_update(authed_client, authed_supplier):
    response = authed_client.patch(
        reverse('supplier'), {'company_email': 'a@b.co'}, format='json'
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['company_email'] == 'a@b.co'


@pytest.mark.django_db
def test_supplier_retrieve_no_supplier(authed_client, authed_supplier):
    authed_supplier.delete()

    response = authed_client.get(reverse('supplier'))

    assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
def test_gecko_num_registered_supplier_view_returns_correct_json():
    client = APIClient()
    models.Supplier.objects.create(**VALID_REQUEST_DATA)
    # Use basic auth with user=gecko and pass=X
    encoded_creds = base64.b64encode(
        'gecko:X'.encode('ascii')).decode("ascii")
    client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded_creds)

    response = client.get(reverse('gecko-total-registered-suppliers'))

    expected = {
        "item": [
            {
              "value": 1,
              "text": "Total registered suppliers"
            }
          ]
    }
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == expected


@pytest.mark.django_db
def test_gecko_num_registered_supplier_view_requires_auth():
    client = APIClient()

    response = client.get(reverse('gecko-total-registered-suppliers'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_gecko_num_registered_supplier_view_rejects_incorrect_creds():
    client = APIClient()
    # correct creds are gecko:X
    encoded_creds = base64.b64encode(
        'user:pass'.encode('ascii')).decode("ascii")
    client.credentials(HTTP_AUTHORIZATION='Basic ' + encoded_creds)

    response = client.get(reverse('gecko-total-registered-suppliers'))

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
@patch('core.tasks.send_email')
def test_unsubscribe_supplier(mock_task, authed_client, authed_supplier):
    response = authed_client.post(reverse('unsubscribe-supplier'))

    authed_supplier.refresh_from_db()
    assert response.status_code == 200
    assert authed_supplier.unsubscribed is True
    assert mock_task.delay.called


@pytest.mark.django_db
@patch('notifications.notifications.supplier_unsubscribed')
def test_unsubscribe_supplier_email_confirmation(
    mock_supplier_unsubscribed, authed_client, authed_supplier
):
    authed_client.post(reverse('unsubscribe-supplier'))

    mock_supplier_unsubscribed.assert_called_once_with(
        supplier=authed_supplier
    )


@pytest.mark.django_db
@patch('core.authentication.Oauth2AuthenticationSSO.authenticate_credentials')
def test_external_supplier_details_get_bearer_auth(
    mock_authenticate_credentials, client, authed_supplier, settings
):
    sso_user = helpers.SSOUser(id=authed_supplier.sso_id, email='test@example.com')
    mock_authenticate_credentials.return_value = (sso_user, '123')

    settings.FAS_COMPANY_PROFILE_URL = 'http://profile/{number}'
    expected = serializers.ExternalSupplierSerializer(authed_supplier).data

    url = reverse('external-supplier-details')
    response = client.get(url, {}, HTTP_AUTHORIZATION='Bearer 123')

    assert response.status_code == 200
    assert response.json() == expected
    assert mock_authenticate_credentials.call_count == 1
    assert mock_authenticate_credentials.call_args == call('123')


@pytest.mark.django_db
def test_external_supplier_details_get_sso_auth(
    authed_client, authed_supplier, settings
):
    settings.FAS_COMPANY_PROFILE_URL = 'http://profile/{number}'
    expected = serializers.ExternalSupplierSerializer(authed_supplier).data

    url = reverse('external-supplier-details')
    response = authed_client.get(url, {})

    assert response.status_code == 200
    assert response.json() == expected


@pytest.mark.django_db
def test_external_supplier_details_post(authed_client):
    response = authed_client.post(
        reverse('external-supplier-details'),
        {},
        HTTP_AUTHORIZATION='Bearer 123'
    )

    assert response.status_code == 405


@pytest.mark.django_db
def test_external_supplier_details_get_no_supplier(
    authed_client, authed_supplier
):

    authed_supplier.delete()

    response = authed_client.get(
        reverse('external-supplier-details'),
        {},
        HTTP_AUTHORIZATION='Bearer 123'
    )

    assert response.status_code == 404


@pytest.mark.django_db
def test_external_supplier_sso_list(authed_client, authed_supplier):

    suppliers = factories.SupplierFactory.create_batch(3)
    url = reverse('external-supplier-sso-list')
    response = authed_client.get(url)

    assert response.status_code == 200
    assert response.json() == [
        suppliers[2].sso_id,
        suppliers[1].sso_id,
        suppliers[0].sso_id,
        authed_supplier.sso_id,
    ]


@pytest.mark.django_db
def test_company_collaborators_anon_users():
    url = reverse('supplier-company-collaborators-list')
    client = APIClient()

    response = client.get(url)

    assert response.status_code == 401


@pytest.mark.django_db
def test_company_collaborators_not_profile_owner(
    authed_supplier, authed_client
):
    authed_supplier.role = user_roles.EDITOR
    authed_supplier.save()

    url = reverse('supplier-company-collaborators-list')

    response = authed_client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_company_collaborators_profile_owner(
    authed_supplier, authed_client
):
    authed_supplier.role = user_roles.ADMIN
    authed_supplier.save()

    supplier_one = factories.SupplierFactory(
        company=authed_supplier.company,
        role=user_roles.EDITOR,
    )
    supplier_two = factories.SupplierFactory(
        company=authed_supplier.company,
        role=user_roles.EDITOR,
    )
    factories.SupplierFactory()

    url = reverse('supplier-company-collaborators-list')

    response = authed_client.get(url)

    assert response.status_code == 200
    parsed = response.json()
    supplier_sso_ids = {supplier_one.sso_id, supplier_two.sso_id, authed_supplier.sso_id}

    assert {supplier['sso_id'] for supplier in parsed} == supplier_sso_ids


@pytest.mark.django_db
def test_company_collaborators_profile_owner_collaborators(
    authed_supplier, authed_client
):
    authed_supplier.role = user_roles.ADMIN
    authed_supplier.save()

    url = reverse('supplier-company-collaborators-list')

    response = authed_client.get(url)

    assert response.status_code == 200
    assert response.json() == [
        serializers.SupplierSerializer(authed_supplier).data
    ]


@pytest.mark.django_db
@patch('sigauth.helpers.RequestSignatureChecker.test_signature',
       Mock(return_value=True))
@patch('core.views.get_file_from_s3')
def test_supplier_csv_dump(mocked_get_file_from_s3, authed_client):
    settings.STORAGE_CLASS_NAME = 'default'
    settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE = 'my_db_buket'
    reload_module('supplier.views')
    reload_module('buyer.views')
    reload_urlconf()

    mocked_body = Mock()
    mocked_body.read.return_value = b'company_name\r\nacme\r\n'
    mocked_get_file_from_s3.return_value = {
        'Body': mocked_body
    }
    response = authed_client.get(
        reverse('supplier-csv-dump'),
        {'token': settings.CSV_DUMP_AUTH_TOKEN}
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.content == b'company_name\r\nacme\r\n'
    assert response._headers['content-type'] == ('Content-Type', 'text/csv')
    assert response._headers['content-disposition'] == (
        'Content-Disposition',
        'attachment; filename="{filename}"'.format(
            filename=settings.SUPPLIERS_CSV_FILE_NAME
        )
    )


@pytest.mark.django_db
def test_disconnect_supplier_sole_admin(authed_supplier, authed_client):
    authed_supplier.role = user_roles.ADMIN
    authed_supplier.save()

    url = reverse('company-disconnect-supplier')

    response = authed_client.post(url)

    assert response.status_code == 400
    assert response.json() == [helpers.MESSAGE_ADMIN_NEEDED]


@pytest.mark.parametrize('role', (user_roles.ADMIN, user_roles.EDITOR, user_roles.MEMBER))
@pytest.mark.django_db
def test_disconnect_supplier_multiple_admin(authed_supplier, authed_client, role):
    authed_supplier.role = role
    authed_supplier.save()
    factories.SupplierFactory(role=user_roles.ADMIN, company=authed_supplier.company)

    url = reverse('company-disconnect-supplier')

    response = authed_client.post(url)

    assert response.status_code == 200

    authed_supplier.refresh_from_db()

    assert authed_supplier.company is None
    assert authed_supplier.role == user_roles.MEMBER


@pytest.mark.django_db
def test_supplier_retrieve_sso_id(client):

    supplier = factories.SupplierFactory()

    url = reverse('supplier-retrieve-sso-id', kwargs={'sso_id': supplier.sso_id})

    response = client.get(url)

    assert response.json()['sso_id'] == supplier.sso_id
