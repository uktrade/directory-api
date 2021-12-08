import attr
import pytest

from dataservices.tests.factories import (
    CIAFactBookFactory,
    ConsumerPriceIndexFactory,
    EaseOfDoingBusiness,
    GDPPerCapitaFactory,
    IncomeFactory,
    SuggestedCountriesFactory,
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    'factory',
    (
        ConsumerPriceIndexFactory,
        EaseOfDoingBusiness,
        GDPPerCapitaFactory,
        IncomeFactory,
    ),
)
@pytest.mark.django_db
def test_model_to_str(factory):
    create_model = factory()
    assert str(create_model) == create_model.country.name


@pytest.mark.django_db
def test_suggested_country_hs_code():
    country = SuggestedCountriesFactory()
    assert str(country) == str(country.hs_code)


@pytest.mark.django_db
def test_cia_factbook_country_name():
    country = CIAFactBookFactory()
    assert str(country) == country.country_name
