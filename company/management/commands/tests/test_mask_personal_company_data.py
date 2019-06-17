import pytest

from django.core.management import call_command

from company.tests import factories
from company.models import Company


@pytest.fixture(autouse=True)
def new_companies():
    new_companies = []
    for _ in range(10):
        new_companies.append(
            factories.CompanyFactory()
        )
    return new_companies


@pytest.mark.django_db
def test_mask_company_data(new_companies):
    call_command('mask_personal_company_data')

    for new_company in new_companies:
        masked_company = Company.objects.get(id=new_company.id)
        assert masked_company.name != new_company.name
        assert masked_company.postal_full_name != new_company.postal_full_name
        assert masked_company.address_line_1 != new_company.address_line_1
        assert masked_company.address_line_2 != new_company.address_line_2
        assert masked_company.postal_code != new_company.postal_code
        assert masked_company.po_box != new_company.po_box
        assert masked_company.email_address != new_company.email_address
        assert masked_company.email_full_name != new_company.email_full_name
