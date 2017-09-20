from rest_framework import status
import pytest

from django.core.urlresolvers import reverse

from exportopportunity import models


@pytest.mark.django_db
def test_export_opportunity_create(authed_client):
    assert models.ExportOpportunity.objects.count() == 0

    data = {
        'additional_requirements': 'give me things',
        'business_model': ['distribution'],
        'business_model_other': 'things',
        'company_name': 'Jim corp',
        'company_website': 'http://www.example.com',
        'contact_preference': ['EMAIL', 'PHONE'],
        'email_address': 'jim@exmaple.com',
        'email_address_confirm': 'jim@exmaple.com',
        'full_name': 'jim example',
        'job_title': 'Exampler',
        'locality': 'France',
        'order_deadline': '1-3 MONTHS',
        'order_size': '1-1000',
        'phone_number': '07507605844',
        'products': ['DISCOUNT'],
        'products_other': 'things',
        'target_sectors': ['retail'],
        'target_sectors_other': 'things',
        'terms_agreed': True,
        'campaign': 'food-is-great',
        'country': 'france',
    }

    response = authed_client.post(
        reverse('export-opportunity-create'),
        data=data
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert models.ExportOpportunity.objects.count() == 1
