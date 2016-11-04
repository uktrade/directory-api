import pytest

from buyer import models


@pytest.fixture
def buyer():
    return models.Buyer.objects.create(
        email='jim@example.com',
        name='Jim Exampleson',
        sector='AEROSPACE',
    )


@pytest.mark.django_db
def test_buyer_name(buyer):
    assert str(buyer) == buyer.name
