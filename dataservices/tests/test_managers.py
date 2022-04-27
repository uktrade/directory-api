import pytest

from dataservices.models import UKTotalTradeByCountry
from dataservices.tests.factories import UKTotalTradeByCountryFactory


@pytest.mark.django_db
def test_uk_total_trade_manager():
    UKTotalTradeByCountryFactory.create_batch(10)

    assert UKTotalTradeByCountry.objects.imports().count() == 5
    assert UKTotalTradeByCountry.objects.exports().count() == 5
