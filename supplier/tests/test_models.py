import pytest

from supplier.models import Supplier
from supplier.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_supplier_model_str():
    supplier = Supplier(**VALID_REQUEST_DATA)

    assert supplier.company_email == str(supplier)
