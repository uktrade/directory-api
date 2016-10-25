import http
from unittest.mock import patch

import requests
import pytest

from rest_framework.serializers import ValidationError

from company import models, validators
from company.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_company_unique_rejects_existing(client):
    models.Company.objects.create(**VALID_REQUEST_DATA)
    with pytest.raises(ValidationError):
        validators.company_unique(VALID_REQUEST_DATA['number'])


@pytest.mark.django_db
def test_company_unique_accepts_new(client):
    assert validators.company_unique('01234567') is None


@patch.object(validators.helpers, 'get_companies_house_profile')
def test_company_active_rejects_not_found(mock_get_companies_house_profile):
    response = requests.Response()
    response.status_code = http.client.NOT_FOUND
    mock_get_companies_house_profile.return_value = response

    with pytest.raises(ValidationError):
        validators.company_active('01234567')


@patch.object(validators.helpers, 'get_companies_house_profile')
def test_company_active_rejects_not_inactive(mock_get_companies_house_profile):
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: {'company_status': 'inactive'}

    mock_get_companies_house_profile.return_value = response
    with pytest.raises(ValidationError):
        validators.company_active('01234567')


@patch.object(validators.helpers, 'get_companies_house_profile')
def test_company_active_accepts_active(mock_get_companies_house_profile):
    response = requests.Response()
    response.status_code = http.client.OK
    response.json = lambda: {'company_status': 'active'}

    mock_get_companies_house_profile.return_value = response
    assert validators.company_active('01234567') is None
