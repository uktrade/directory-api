import pytest

from dataservices.models import UKTotalTradeByCountry
from dataservices.tests.factories import (
    CIAFactBookFactory,
    ConsumerPriceIndexFactory,
    EaseOfDoingBusiness,
    GDPPerCapitaFactory,
    IncomeFactory,
    InternetUsageFactory,
    SuggestedCountriesFactory,
    UKTotalTradeByCountryFactory,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'factory',
    (
        ConsumerPriceIndexFactory,
        EaseOfDoingBusiness,
        GDPPerCapitaFactory,
        IncomeFactory,
        InternetUsageFactory,
    ),
)
@pytest.mark.django_db
def test_model_to_str(factory):
    create_model = factory()
    assert str(create_model) == f'{create_model.country.name}:{create_model.year}'


@pytest.mark.django_db
def test_suggested_country_hs_code():
    country = SuggestedCountriesFactory()
    assert str(country) == str(country.hs_code)


@pytest.mark.django_db
def test_cia_factbook_country_name():
    country = CIAFactBookFactory()
    assert str(country) == country.country_name


@pytest.mark.django_db
def test_uk_total_trade_manager():
    UKTotalTradeByCountryFactory.create_batch(10)

    assert UKTotalTradeByCountry.objects.imports().count() == 5
    assert UKTotalTradeByCountry.objects.exports().count() == 5
    assert UKTotalTradeByCountry.objects.goods().count() == 5
    assert UKTotalTradeByCountry.objects.services().count() == 5
