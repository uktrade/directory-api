from unittest import mock

import pytest
from directory_constants import user_roles
from django.core import signing
from django.urls import reverse
from rest_framework.test import APIClient

from company.models import Company, CompanyUser
from company.tests.factories import CompanyFactory
from enrolment.tests.factories import PreVerifiedEnrolmentFactory


@pytest.fixture
def default_enrolment_data():
    return {
        "sso_id": 1,
        "company_number": "01234567",
        "company_email": "test@example.com",
        "contact_email_address": "test@example.com",
        "company_name": "Test Corp",
        "referrer": "company_email",
        "has_exported_before": True,
        "date_of_creation": "2010-10-10",
        "mobile_number": '07507605137',
        "revenue": "101010.00",
    }


@pytest.mark.django_db
@mock.patch('company.helpers.send_registration_letter')
def test_enrolment_viewset_create(mock_send_registration_letter, settings):
    settings.FEATURE_REGISTRATION_LETTERS_ENABLED = True
    data = {
        'address_line_1': '123 Fake street',
        'address_line_2': 'The Lane',
        'company_name': 'Example Corp.',
        'company_number': '07504387',
        'company_email': 'jim@example.com',
        'contact_email_address': 'jim@example.com',
        'country': 'UK',
        'has_exported_before': True,
        'locality': 'London',
        'po_box': 'PO 344',
        'postal_code': 'E14 POX',
        'sso_id': 1,
    }
    response = APIClient().post(reverse('enrolment'), data, format='json')

    assert response.status_code == 201

    company = Company.objects.get(number='07504387')
    assert company.address_line_1 == data['address_line_1']
    assert company.address_line_2 == data['address_line_2']
    assert company.name == data['company_name']
    assert company.number == data['company_number']
    assert company.email_address == data['contact_email_address']
    assert company.country == data['country']
    assert company.has_exported_before == data['has_exported_before']
    assert company.locality == data['locality']
    assert company.po_box == data['po_box']
    assert company.postal_code == data['postal_code']

    supplier = CompanyUser.objects.get(sso_id=1)
    assert supplier.company == company
    assert supplier.company_email == data['contact_email_address']
    assert supplier.sso_id == data['sso_id']
    assert supplier.role == user_roles.ADMIN

    assert mock_send_registration_letter.call_count == 1
    assert mock_send_registration_letter.call_args == mock.call(
        company=company,
        form_url='send_company_claimed_letter_automatically_sent',
    )


@pytest.mark.django_db
def test_enrolment_viewset_create_optional_fields_unset():

    data = {
        'company_name': 'Example Corp.',
        'company_number': '07504387',
        'company_email': 'jim@example.com',
        'contact_email_address': 'jim@example.com',
        'has_exported_before': True,
        'sso_id': 1,
    }
    response = APIClient().post(reverse('enrolment'), data, format='json')

    assert response.status_code == 201

    company = Company.objects.get(number='07504387')
    assert company.address_line_1 == ''
    assert company.address_line_2 == ''
    assert company.name == data['company_name']
    assert company.number == data['company_number']
    assert company.email_address == data['contact_email_address']
    assert company.country == ''
    assert company.has_exported_before == data['has_exported_before']
    assert company.locality == ''
    assert company.po_box == ''
    assert company.postal_code == ''

    supplier = CompanyUser.objects.get(sso_id=1)
    assert supplier.company == company
    assert supplier.company_email == data['contact_email_address']
    assert supplier.sso_id == data['sso_id']


@pytest.mark.django_db
def test_enrolment_viewset_create_invalid_data(default_enrolment_data, client):
    del default_enrolment_data['company_name']
    response = client.post(reverse('enrolment'), default_enrolment_data, format='json')

    assert response.status_code == 400
    assert response.json() == {'company_name': ['This field is required.']}


@pytest.mark.django_db
@mock.patch('enrolment.serializers.CompanyEnrolmentSerializer.create', side_effect=Exception('!'))
def test_enrolment_create_company_exception_rollback(mock_create, default_enrolment_data, client):
    with pytest.raises(Exception):
        client.post(reverse('enrolment'), default_enrolment_data, format='json')

    assert Company.objects.count() == 0
    assert CompanyUser.objects.count() == 0


@pytest.mark.django_db
@mock.patch('company.serializers.CompanyUserSerializer.create', side_effect=Exception('!'))
def test_enrolment_create_supplier_exception_rollback(mock_create, default_enrolment_data, client):
    client.post(reverse('enrolment'), default_enrolment_data, format='json')

    assert Company.objects.count() == 0
    assert CompanyUser.objects.count() == 0


@pytest.mark.django_db
def test_enrolment_create_preverified_enrolment(default_enrolment_data):
    preverified_enrolment = PreVerifiedEnrolmentFactory.create(
        company_number=default_enrolment_data['company_number'],
        email_address=default_enrolment_data['contact_email_address'],
    )
    assert preverified_enrolment.is_active is True

    response = APIClient().post(reverse('enrolment'), default_enrolment_data, format='json')

    assert response.status_code == 201

    company = Company.objects.last()
    preverified_enrolment.refresh_from_db()
    assert preverified_enrolment.is_active is True
    assert company.verified_with_preverified_enrolment is False


@pytest.mark.django_db
@mock.patch.object(Company.objects, 'create', side_effect=Exception('!'))
def test_enrolment_create_rollback(mock_update, default_enrolment_data, client):
    preverified_enrolment = PreVerifiedEnrolmentFactory.create(
        company_number=default_enrolment_data['company_number'],
        email_address=default_enrolment_data['contact_email_address'],
    )
    assert preverified_enrolment.is_active is True

    with pytest.raises(Exception):
        client.post(reverse('enrolment'), default_enrolment_data, format='json')

    preverified_enrolment.refresh_from_db()
    assert preverified_enrolment.is_active is True

    assert Company.objects.count() == 0


@pytest.mark.django_db
def test_preverified_enrolment_retrieve_not_found(authed_client, default_enrolment_data):
    preverified_enrolment = PreVerifiedEnrolmentFactory.create(
        company_number=default_enrolment_data['company_number'],
        email_address='jim@thing.com',
    )

    url = reverse('pre-verified-enrolment')
    params = {
        'email_address': preverified_enrolment.email_address,
        'company_number': '1122',
    }
    response = authed_client.get(url, params)

    assert response.status_code == 404


@pytest.mark.django_db
def test_preverified_enrolment_retrieve_found(authed_client, default_enrolment_data):
    preverified_enrolment = PreVerifiedEnrolmentFactory.create(
        company_number=default_enrolment_data['company_number'],
        email_address=default_enrolment_data['contact_email_address'],
    )

    url = reverse('pre-verified-enrolment')
    params = {
        'email_address': preverified_enrolment.email_address,
        'company_number': preverified_enrolment.company_number,
    }
    response = authed_client.get(url, params)

    assert response.status_code == 200


@pytest.mark.django_db
def test_preverified_claim_company_bad_key(authed_client):
    url = reverse('enrolment-claim-preverified', kwargs={'key': '123'})
    response = authed_client.post(url, {'name': 'Foo bar'})

    assert response.status_code == 404


@pytest.mark.django_db
def test_preverified_claim_company_succcess(authed_client):
    CompanyUser.objects.all().delete()
    assert CompanyUser.objects.count() == 0

    company = CompanyFactory()

    url = reverse('enrolment-claim-preverified', kwargs={'key': signing.Signer().sign(company.number)})

    response = authed_client.post(url, {'name': 'Foo bar'})

    assert response.status_code == 201
    assert CompanyUser.objects.count() == 1

    user = CompanyUser.objects.first()
    assert user.name == 'Foo bar'
    assert user.company == company
    assert user.role == user_roles.ADMIN

    company.refresh_from_db()
    assert company.verified_with_preverified_enrolment is True


@pytest.mark.django_db
def test_preverified_retrieve_company_succcess(authed_client):
    company = CompanyFactory()

    url = reverse('enrolment-preverified', kwargs={'key': signing.Signer().sign(company.number)})

    response = authed_client.get(url)

    assert response.status_code == 200


@pytest.mark.django_db
def test_preverified_cretrieve_company_bad_key(authed_client):
    url = reverse('enrolment-preverified', kwargs={'key': '1234'})
    response = authed_client.get(url)

    assert response.status_code == 404
