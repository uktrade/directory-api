import pytest
from django.core.exceptions import ValidationError

from dataservices import models
from dataservices.tests.factories import (
    CIAFactBookFactory,
    ConsumerPriceIndexFactory,
    CountryFactory,
    EaseOfDoingBusiness,
    GDPPerCapitaFactory,
    IncomeFactory,
    InternetUsageFactory,
    MetadataFactory,
    SuggestedCountriesFactory,
    WorldEconomicOutlookByCountryFactory,
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
def test_world_economic_outlook_by_country_is_projection():
    non_projected = WorldEconomicOutlookByCountryFactory(year=1999, estimates_start_after=2000)
    assert non_projected.is_projection is False

    non_projected = WorldEconomicOutlookByCountryFactory(year=2000, estimates_start_after=2000)
    assert non_projected.is_projection is False

    projected = WorldEconomicOutlookByCountryFactory(year=2001, estimates_start_after=2000)
    assert projected.is_projection is True


@pytest.mark.django_db
def test_metadata_view_name():
    metadata = MetadataFactory(view_name='MyView')

    assert str(metadata) == 'MyView'


@pytest.mark.django_db
def test_uk_free_trade_agreement_no_name():
    fta = models.UKFreeTradeAgreement()
    with pytest.raises(ValidationError):
        fta.clean_fields()

    fta.country = CountryFactory()

    assert fta.name == ''

    fta.clean_fields()

    assert fta.name == fta.country.name
