import pytest
from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status

from directory_constants.constants import exred_sector_names

from .factories import TriageResultFactory


@freeze_time('2016-11-23T11:21:10.977518Z')
@pytest.mark.django_db
def test_triage_result_retrieve_view(authed_client, authed_supplier):
    triage_result = TriageResultFactory(
        sso_id=authed_supplier.sso_id
    )
    response = authed_client.get(
        reverse('export-readiness-triage-create-retrieve')
    )

    assert response.status_code == status.HTTP_200_OK
    expected_response = {
        'company_name': triage_result.company_name,
        'created': '2016-11-23T11:21:10.977518Z',
        'exported_before': triage_result.exported_before,
        'regular_exporter': triage_result.regular_exporter,
        'used_online_marketplace': triage_result.used_online_marketplace,
        'id': triage_result.pk,
        'modified': '2016-11-23T11:21:10.977518Z',
        'sector': triage_result.sector,
        'sector_name': triage_result.sector_name,
        'sole_trader': triage_result.sole_trader,
        'sso_id': triage_result.sso_id
    }
    assert response.json() == expected_response


@pytest.mark.django_db
def test_triage_result_retrieve_view_404(authed_client):
    response = authed_client.get(
        reverse('export-readiness-triage-create-retrieve')
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


@freeze_time('2016-11-23T11:21:10.977518Z')
@pytest.mark.django_db
def test_triage_result_create_view(authed_client):
    triage_result_data = {
        'company_name': 'Acme ltd',
        'exported_before': True,
        'regular_exporter': True,
        'used_online_marketplace': True,
        'sector': exred_sector_names.SECTORS_CHOICES[0][0],
        'sole_trader': False,
    }

    response = authed_client.post(
        reverse('export-readiness-triage-create-retrieve'),
        triage_result_data,
    )
    assert response.status_code == status.HTTP_201_CREATED
    expected_response = {
        'company_name': 'Acme ltd',
        'created': '2016-11-23T11:21:10.977518Z',
        'exported_before': True,
        'regular_exporter': True,
        'used_online_marketplace': True,
        'id': response.json()['id'],
        'modified': '2016-11-23T11:21:10.977518Z',
        'sector': exred_sector_names.SECTORS_CHOICES[0][0],  # HS01
        # Animals: Live
        'sector_name': exred_sector_names.SECTORS_CHOICES[0][1],
        'sole_trader': False,
        'sso_id': 999
    }
    assert response.json() == expected_response
