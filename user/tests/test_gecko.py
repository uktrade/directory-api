import pytest

from user import gecko
from user.models import User


@pytest.mark.django_db
def test_gecko_num_registered_user_correct():
    User.objects.bulk_create([
        User(sso_id=1, company_email='1@example.com', mobile_number='1'),
        User(sso_id=2, company_email='2@example.com', mobile_number='2'),
        User(sso_id=3, company_email='3@example.com', mobile_number='3'),
    ])

    gecko_json = gecko.total_registered_users()

    expected = {
      "item": [
        {
          "value": 3,
          "text": "Total registered users"
        }
      ]
    }
    assert gecko_json == expected
