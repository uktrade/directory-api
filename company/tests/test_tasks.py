from unittest.mock import patch

import pytest

from company.models import Company
from company.tasks import save_company_to_elasticsearch
from company.tests.factories import CompanyFactory


@pytest.mark.django_db
@patch.object(Company, 'to_doc_type')
def test_save_to_elasticsearch(mocked_to_doc_type):
    company = CompanyFactory()
    save_company_to_elasticsearch(company_id=company.id)

    assert mocked_to_doc_type().save.called is True
