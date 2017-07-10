from unittest.mock import patch, Mock

from rest_framework import status
import pytest

from django.core.urlresolvers import reverse

from exportopportunity import constants, models


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_export_opportunity_create(authed_client):
    assert models.ExportOpportunity.objects.count() == 0

    response = authed_client.post(reverse('export-opportunity-create'))

    data = {
        'type_of_enquiry': constants.OPEN_ENDED,
        'open_ended_description': 'foobar',
        'business_model': constants.DISTRIBUTION,
        'subsector': constants.CATERING,
        'bid_value': 'badzillions',
        'bid_timing': '2017-09-09',
        'full_name': 'Testo Useri',
        'email_address': 'test@foo.com',
        'company_name': 'Acme'
    }

    response = authed_client.post(
        reverse('export-opportunity-create'),
        data=data
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert models.ExportOpportunity.objects.count() == 1
