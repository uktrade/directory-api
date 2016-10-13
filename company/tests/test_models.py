import pytest

from company.models import Company
from company.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_company_model_str():
    company = Company(**VALID_REQUEST_DATA)

    assert company.name == str(company)
