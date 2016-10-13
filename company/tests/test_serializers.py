import pytest

from company.serializers import CompanySerializer
from company.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_company_serializer_save():
    serializer = CompanySerializer(data=VALID_REQUEST_DATA)
    serializer.is_valid()

    company = serializer.save()

    assert company.name == VALID_REQUEST_DATA['name']
    assert company.number == VALID_REQUEST_DATA['number']
    assert company.website == VALID_REQUEST_DATA['website']
    assert company.description == VALID_REQUEST_DATA['description']
    assert company.aims == VALID_REQUEST_DATA['aims']
