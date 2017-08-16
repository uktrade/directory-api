from directory_constants.constants import choices
from rest_framework import status
import pytest

from django.core.urlresolvers import reverse

from exportopportunity import models


@pytest.mark.django_db
def test_export_opportunity_create(authed_client):
    assert models.ExportOpportunity.objects.count() == 0

    data = {
        'type_of_enquiry': choices.OPEN_ENDED,
        'open_ended_description': 'foobar',
        'business_model': choices.DISTRIBUTION,
        'subsector': choices.CATERING,
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
