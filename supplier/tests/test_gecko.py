import pytest

from supplier import gecko
from user.models import User as Supplier


@pytest.mark.django_db
def test_gecko_num_registered_supplier_correct():
    Supplier.objects.bulk_create([
        Supplier(sso_id=1, company_email='1@example.com', mobile_number='1'),
        Supplier(sso_id=2, company_email='2@example.com', mobile_number='2'),
        Supplier(sso_id=3, company_email='3@example.com', mobile_number='3'),
    ])

    gecko_json = gecko.total_registered_suppliers()

    expected = {
      "item": [
        {
          "value": 3,
          "text": "Total registered suppliers"
        }
      ]
    }
    assert gecko_json == expected
