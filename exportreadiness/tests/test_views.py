import pytest
from django.urls import reverse
from freezegun import freeze_time
from rest_framework import status

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
        'exporting_regular_part': triage_result.exporting_regular_part,
        'id': triage_result.pk,
        'modified': '2016-11-23T11:21:10.977518Z',
        'sector': triage_result.sector,
        'sole_trader': triage_result.sole_trader,
        'sso_id': triage_result.sso_id
    }
    assert response.json() == expected_response
