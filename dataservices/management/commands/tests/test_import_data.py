import datetime
import re
from itertools import cycle, islice
from unittest import mock

import pandas as pd
import pytest
from django.core import management
from django.test import override_settings
from import_export import results

from conf import settings
from dataservices import models


@pytest.mark.django_db
@pytest.mark.parametrize(
    'model_name, management_cmd, object_count, de_rows',
    (
        (models.CorruptionPerceptionsIndex, 'import_cpi_data', 181, 1),
        (models.WorldEconomicOutlook, 'import_weo_data', 1552, 0),
    ),
)
def test_import_data_sets(model_name, management_cmd, object_count, de_rows):
    model_name.objects.create(country_name='abc', country_code='a')
    models.Country.objects.create(name='Germ', iso2='DE', iso3='DEU')
    management.call_command(management_cmd)
    assert model_name.objects.count() == object_count
    assert model_name.objects.filter(country__iso2='DE').count() == de_rows


@pytest.mark.django_db
@mock.patch.object(results.Result, 'has_errors', mock.Mock(return_value=True))
def test_error_import_data_sets_error():
    management.call_command('import_weo_data')
    assert models.CorruptionPerceptionsIndex.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'model_name, management_cmd, object_count',
    (
        (models.Country, 'import_countries', 195),
        (models.RuleOfLaw, 'import_rank_of_law_data', 131),
        (models.Currency, 'import_currency_data', 269),
        (models.TradingBlocs, 'import_trading_blocs', 356),
    ),
)
def test_import_countries_data_sets(model_name, management_cmd, object_count):
    management.call_command(management_cmd)
    assert model_name.objects.count() == object_count


@pytest.mark.django_db
def test_import_country_data_crud():
    from dataservices.tests import factories

    old_country = factories.CountryFactory(is_active=True)
    change_country = factories.CountryFactory(name='Ital', iso2='IT')
    factories.CountryFactory(name='Maldives', iso2='MV', iso1=462, iso3='MDV', region='South Asia')
    inactive_country = factories.CountryFactory(
        name='India', iso2='IN', iso1=356, iso3='IND', region='South Asia', is_active=False
    )
    management.call_command('import_countries', 'dataservices/tests/fixtures/import-countries-crud-test.csv')

    old_country.refresh_from_db()
    change_country.refresh_from_db()
    inactive_country.refresh_from_db()

    assert models.Country.objects.all().count() == 5
    assert models.Country.objects.filter(is_active=True).count() == 4
    assert change_country.name == 'Italy'
    assert change_country.iso2 == 'IT'
    assert change_country.iso1 == '380'
    assert change_country.iso3 == 'ITA'
    assert change_country.region == 'Europe'
    assert change_country.is_active is True
    assert old_country.is_active is False
    assert inactive_country.is_active is True


@pytest.mark.django_db
def test_import_rank_of_law_data_with_no_country():
    management.call_command('import_rank_of_law_data')
    management.call_command('import_currency_data')
    rule_of_law = models.RuleOfLaw.objects.first()
    currencies_data = models.Currency.objects.first()
    assert rule_of_law.country is None
    assert currencies_data.country is None


@pytest.mark.django_db
def test_import_all():
    models.SuggestedCountry.objects.count() == 0
    management.call_command('import_all')
    models.SuggestedCountry.objects.count() == 493


@pytest.mark.django_db
def test_import_comtrade():
    management.call_command('import_countries')
    management.call_command('import_comtrade_data', '--test')
    data = models.ComtradeReport.objects.filter(country_iso3='FRA', year='2019', commodity_code='010649')
    assert len(models.ComtradeReport.objects.all()) == 1000
    assert data.first().country.iso3 == 'FRA'
    assert data.first().commodity_code == '010649'
    assert len(data) == 2
    assert data.first().trade_value == 9189567
    assert data.first().country_id is not None
    management.call_command('import_comtrade_data', '--unlink_countries')
    assert data.first().country_id is None
    management.call_command('import_comtrade_data', '--link_countries')
    assert data.first().country_id is not None


@pytest.mark.django_db
def test_import_raw_comtrade():
    management.call_command('import_comtrade_data', '--raw', 'dataservices/resources/comtrade_sample.csv')
    data = models.ComtradeReport.objects.filter(country_iso3='FRA', commodity_code='390720')
    assert len(models.ComtradeReport.objects.all()) == 389
    assert len(data) == 2
    assert str(data.first()) == 'FRA:390720'
    assert data.first().country_iso3 == 'FRA'
    assert data.first().commodity_code == '390720'
    assert data.first().trade_value == 345434516
    assert data.first().uk_or_world == 'WLD'
    assert data[1].uk_or_world == 'GBR'

    management.call_command('import_comtrade_data', '--wipe')
    assert len(models.ComtradeReport.objects.all()) == 0


@pytest.mark.django_db
def test_import_target_age_groups():
    management.call_command('import_countries')
    management.call_command('import_target_age_groups')
    data = models.PopulationData.objects.filter(country__iso1=276, year=2020)
    assert len(models.PopulationData.objects.all()) == 40986
    assert data.first().country.iso1 == '276'
    assert len(data) == 2
    assert data.first().age_100_plus == 4
    data = models.PopulationData.objects.filter(country__iso2='BE', year=2020)
    assert data.first().country.name == 'Belgium'


@pytest.mark.django_db
def test_import_urban_rural_population():
    management.call_command('import_countries')
    management.call_command('import_population_urbanrural')
    data = models.PopulationUrbanRural.objects.filter(country__iso3='DEU', year=2020)
    assert len(models.PopulationUrbanRural.objects.all()) == 3822
    assert data.first().country.name == 'Germany'
    assert str(data[0]) == 'Germany:urban'
    assert str(data[1]) == 'Germany:rural'
    assert len(data) == 2
    assert data[0].value == 63930
    assert data[0].urban_rural == 'urban'
    assert data[1].value == 18610
    assert data[1].urban_rural == 'rural'
    data = models.PopulationUrbanRural.objects.filter(country__iso3='BEL', year=2020)
    assert data.first().country.name == 'Belgium'


@pytest.mark.django_db
def test_import_factbook():
    management.call_command('import_countries')
    management.call_command('import_cia_factbook_data')
    data = models.CIAFactbook.objects.get(country__iso3='DEU')
    assert len(models.CIAFactbook.objects.all()) == 259
    assert data.country.name == 'Germany'
    assert data.factbook_data.get('people').get('languages').get('language')[0] == {
        'name': 'German',
        'note': 'official',
    }


@pytest.fixture
def world_bank_mock(requests_mocker):
    def mock_request(loader_file):
        with open(f'dataservices/tests/fixtures/{loader_file}.zip', 'rb') as f:
            return requests_mocker.get(
                re.compile(f'{settings.WORLD_BANK_API_URI}*'),
                status_code=200,
                content=f.read(),
            )

    return mock_request


@pytest.mark.django_db
@pytest.mark.parametrize(
    'model_name, load_name, object_count',
    (
        (models.ConsumerPriceIndex, 'consumerpriceindex', 20),
        (models.GDPPerCapita, 'gdpcapita', 5),
        (models.EaseOfDoingBusiness, 'easeofdoingbusiness', 2),
        (models.Income, 'income', 4),
        (models.InternetUsage, 'internetusage', 7),
    ),
)
@pytest.mark.django_db
def test_import_worldbank_data(world_bank_mock, model_name, load_name, object_count):
    world_bank_mock(load_name)
    management.call_command('import_countries')
    management.call_command('import_worldbank_data', load_name)
    assert len(model_name.objects.all()) == object_count


@pytest.mark.django_db
def test_import_worldbank_data_unknown_cmd():
    management.call_command('import_countries')
    management.call_command('import_worldbank_data', 'bad_load')


@pytest.mark.django_db
def test_import_worldbank_data_all(world_bank_mock):
    world_bank_mock('easeofdoingbusiness')
    management.call_command('import_countries')
    management.call_command('import_worldbank_data', 'all')


@pytest.fixture()
def trade_in_services_raw_data():
    return {
        'iso2': ['CN', 'CN', 'CN', 'CN', 'CN', 'CN', 'XX'],
        'period': [
            'quarter/2021-Q1',
            'quarter/2021-Q2',
            'quarter/2021-Q3',
            'quarter/2021-Q4',
            'quarter/2022-Q1',
            'year/2021',
            'quarter/2021-Q1',
        ],
        'period_type': ['quarter', 'quarter', 'quarter', 'quarter', 'quarter', 'year', 'quarter'],
        'service_code': [1, 1, 1, 1, 1, 1, 1],
        'service_name': [
            'Manufacturing',
            'Manufacturing',
            'Manufacturing',
            'Manufacturing',
            'Manufacturing',
            'Manufacturing',
            'Manufacturing',
        ],
        'imports': [1.0, 2.0, 3.0, 3.0, 2.0, 9.0, 1.0],
        'exports': [1.0, 2.0, 3.0, 3.0, 2.0, 9.0, 1.0],
    }


@pytest.fixture()
def trade_in_goods_by_quarter_raw_data():
    return {
        'iso2': ['CN', 'CN', 'CN', 'CN', 'CN', 'CN', 'XX'],
        'period': [
            'quarter/2021-Q1',
            'quarter/2021-Q2',
            'quarter/2021-Q3',
            'quarter/2022-Q1',
            'quarter/2022-Q2',
            'quarter/2022-Q3',
            'quarter/2021-Q1',
        ],
        'commodity_code': [1, 1, 1, 1, 1, 1, 1],
        'commodity_name': [
            'Aircraft',
            'Aircraft',
            'Aircraft',
            'Aircraft',
            'Aircraft',
            'Aircraft',
            'Aircraft',
        ],
        'imports': [1.0, 2.0, 3.0, 3.0, 2.0, None, 1.0],
        'exports': [1.0, 2.0, 3.0, 3.0, 2.0, None, 1.0],
    }


@pytest.fixture()
def world_economic_outlook_raw_data():
    return {
        'ons_iso_alpha_3_code': 'CHN CHN CHN CHN GBR GBR GBR GBR XXX XXX'.split(),
        'subject_code': list(islice(cycle('NGDPDPC NGDP_RPCH'.split()), 10)),
        'subject_descriptor': list(islice(cycle(['GDP, current prices', 'GDP, constant prices']), 10)),
        'subject_notes': list(islice(cycle(['GDP is in U.S. dollars per person', 'Annual percentages of GDP']), 10)),
        'units': list(islice(cycle(['USD', 'Percent']), 10)),
        'scale': list(islice(cycle(['Units', '']), 10)),
        'year': list(islice(cycle([2020, 2020, 2021, 2021]), 10)),
        'value': [10525.001, 2.244, 12358.797, 8.080, 41127.443, -9.270, 47202.581, 7.441, 12345.001, 1.234],
        'estimates_start_after': [2020, 2021, 2020, 2021, 2019, 2020, 2019, 2020, 2019, 2019],
    }


@pytest.fixture()
def metadata_last_release_raw_data():
    return {
        'table_name': 'trade__uk_goods_nsa trade__uk_services_nsa trade__uk_totals_sa xxx'.split(),
        'last_release': [
            datetime.date(2018, 12, 30),
            datetime.date(2019, 12, 30),
            datetime.date(2020, 12, 30),
            datetime.date(2021, 12, 30),
        ],
    }


@pytest.mark.django_db
@mock.patch('pandas.read_sql')
@override_settings(DATA_WORKSPACE_DATASETS_URL='postgresql://')
def test_import_uk_total_trade_data(read_sql_mock):
    mock_data = {
        'ons_iso_alpha_2_code': ['CN', 'CN', 'CN', 'CN', 'CN', 'CN', 'XX'],
        'period': ['2021-Q1', '2021-Q2', '2021-Q3', '2021-Q4', '2022-Q1', '2022-Q2', '2021-Q1'],
        'imports': [1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
        'exports': [1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
    }
    read_sql_mock.return_value = [pd.DataFrame(mock_data)]

    assert len(models.UKTotalTradeByCountry.objects.all()) == 0

    management.call_command('import_countries')

    # Dry run
    management.call_command('import_uk_total_trade_data')

    assert len(models.UKTotalTradeByCountry.objects.all()) == 0

    # Write option
    management.call_command('import_uk_total_trade_data', '--write')

    assert len(models.UKTotalTradeByCountry.objects.all()) == 7


@pytest.mark.django_db
@mock.patch('pandas.read_sql')
@override_settings(DATA_WORKSPACE_DATASETS_URL='postgresql://')
def test_import_uk_trade_in_services_data(read_sql_mock, trade_in_services_raw_data):
    read_sql_mock.return_value = [pd.DataFrame(trade_in_services_raw_data)]

    assert len(models.UKTradeInServicesByCountry.objects.all()) == 0

    management.call_command('import_countries')

    # Dry run
    management.call_command('import_uk_trade_in_services_data')

    assert len(models.UKTradeInServicesByCountry.objects.all()) == 0

    # Write option
    management.call_command('import_uk_trade_in_services_data', '--write')

    assert len(models.UKTradeInServicesByCountry.objects.all()) == 6


@pytest.mark.django_db
@mock.patch('pandas.read_sql')
@override_settings(DATA_WORKSPACE_DATASETS_URL='postgresql://')
def test_import_uk_trade_in_goods_data(read_sql_mock, trade_in_goods_by_quarter_raw_data):
    read_sql_mock.return_value = [pd.DataFrame(trade_in_goods_by_quarter_raw_data)]

    assert len(models.UKTradeInGoodsByCountry.objects.all()) == 0

    management.call_command('import_countries')

    # Dry run
    management.call_command('import_uk_trade_in_goods_data')

    assert len(models.UKTradeInGoodsByCountry.objects.all()) == 0

    # Write option
    management.call_command('import_uk_trade_in_goods_data', '--write')

    assert len(models.UKTradeInGoodsByCountry.objects.all()) == 6


@pytest.mark.django_db
@mock.patch('pandas.read_sql')
@override_settings(DATA_WORKSPACE_DATASETS_URL='postgresql://')
def test_import_world_economic_outlook_data(read_sql_mock, world_economic_outlook_raw_data):
    read_sql_mock.return_value = [pd.DataFrame(world_economic_outlook_raw_data)]

    assert len(models.WorldEconomicOutlookByCountry.objects.all()) == 0

    management.call_command('import_countries')
    management.call_command('import_world_economic_outlook_data')

    assert len(models.WorldEconomicOutlookByCountry.objects.all()) == 10


@pytest.mark.django_db
@mock.patch('pandas.read_sql')
@override_settings(DATA_WORKSPACE_DATASETS_URL='postgresql://')
def test_import_metadata_source_data(read_sql_mock, metadata_last_release_raw_data):
    read_sql_mock.return_value = pd.DataFrame(metadata_last_release_raw_data)

    assert len(models.Metadata.objects.all()) == 0

    management.call_command('import_metadata_source_data')

    assert len(models.Metadata.objects.all()) == 4


@pytest.mark.django_db
@mock.patch('dataservices.management.commands.import_market_guides_data.call_command')
def test_import_market_guides_data(mock_call_command):
    command_list = [
        'import_uk_total_trade_data',
        'import_uk_trade_in_goods_data',
        'import_uk_trade_in_services_data',
    ]

    management.call_command('import_market_guides_data', '--write')

    assert mock_call_command.call_count == 3

    for idx, command in enumerate(command_list):
        assert command in str(mock_call_command.call_args_list[idx])
        assert 'write=True' in str(mock_call_command.call_args_list[idx])


@pytest.mark.django_db
@mock.patch('dataservices.management.commands.import_market_guides_data.call_command')
def test_import_market_guides_data_dry_run(mock_call_command):
    command_list = [
        'import_uk_total_trade_data',
        'import_uk_trade_in_goods_data',
        'import_uk_trade_in_services_data',
    ]

    management.call_command('import_market_guides_data')

    assert mock_call_command.call_count == 3

    for idx, command in enumerate(command_list):
        assert command in str(mock_call_command.call_args_list[idx])
        assert 'write=False' in str(mock_call_command.call_args_list[idx])
