import pytest

from dataservices.tests.factories import CIAFactBookFactory, ConsumerPriceIndexFactory, SuggestedCountriesFactory


@pytest.mark.django_db
def test_suggested_country_hs_code():
    country = SuggestedCountriesFactory()
    assert str(country) == str(country.hs_code)


@pytest.mark.django_db
def test_cia_factbook_country_name():
    country = CIAFactBookFactory()
    assert str(country) == country.country_name


@pytest.mark.django_db
def test_consumer_price_index():
    cpi = ConsumerPriceIndexFactory()
    assert str(cpi) == cpi.country_name
