import json
import re
from datetime import date, datetime
from itertools import cycle, islice
from unittest import mock

import pandas as pd
import pytest
import sqlalchemy
from django.core import management
from django.core.cache import cache
from django.test import override_settings
from freezegun import freeze_time
from import_export import results
from sqlalchemy import TIMESTAMP, Column, MetaData, String, Table

from conf import settings
from dataservices import models
from dataservices.management.commands.helpers import MarketGuidesDataIngestionCommand
from dataservices.management.commands.import_markets_countries_territories import Command as command_imct
from dataservices.management.commands.import_metadata_source_data import Command as command_imsd


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
        (models.Country, 'import_countries', 196),
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

    cache.clear()

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
@mock.patch('dataservices.management.commands.import_suggested_countries.get_s3_file_stream')
def test_import_all(mock_get_s3_file_stream):
    # Mock the S3 file stream to return a mock CSV data
    mock_csv_data = """HS Code,Country 1,Country 2,Country 3
1234,US,CA,MX
5678,GB,FR,DE
"""
    mock_get_s3_file_stream.return_value = mock_csv_data

    models.SuggestedCountry.objects.count() == 0
    management.call_command('import_all')
    models.SuggestedCountry.objects.count() == 493


@pytest.mark.django_db
@mock.patch('dataservices.management.commands.import_comtrade_data.get_s3_file_stream')
def test_import_raw_comtrade(mock_get_s3_file_stream):
    # Mock the S3 file stream to return a mock CSV data
    mock_csv_data = """id,year,classification,commodity_code,trade_value,uk_or_world,country_iso3
1,2019,HS,390720,345434516,WLD,FRA
2,2019,HS,390720,123456789,GBR,FRA
"""
    mock_get_s3_file_stream.return_value = mock_csv_data

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

    management.call_command('import_comtrade_data', '--wipe', '--period=2019')
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
            date(2018, 12, 30),
            date(2019, 12, 30),
            date(2020, 12, 30),
            date(2021, 12, 30),
        ],
    }


def test_import_metadata_source_data_filter_tables():
    table_names_view_names = {
        't1': ['v1'],
        't2': ['v2'],
    }
    cmd = command_imsd()
    options_none = {'table': None}
    skipped_none = cmd.filter_tables(options_none, table_names_view_names)
    assert skipped_none == table_names_view_names
    options_skip = {'table': 't9'}
    skipped = cmd.filter_tables(options_skip, table_names_view_names)
    assert len(skipped) == 0
    options_add = {'table': 't1'}
    added = cmd.filter_tables(options_add, table_names_view_names)
    assert len(added) == 1


@pytest.mark.django_db
@mock.patch('dataservices.management.commands.import_market_guides_data.call_command')
@mock.patch('dataservices.management.commands.helpers.MarketGuidesDataIngestionCommand.should_ingestion_run')
def test_import_market_guides_data(mock_should_run, mock_call_command):
    command_list = [
        'import_uk_total_trade_data',
        'import_uk_trade_in_goods_data',
        'import_uk_trade_in_services_data',
        'import_world_economic_outlook_data',
    ]
    mock_should_run.return_value = False
    management.call_command('import_market_guides_data', '--write')
    assert mock_call_command.call_count == 0

    mock_should_run.return_value = True
    management.call_command('import_market_guides_data', '--write')
    assert mock_call_command.call_count == 8

    for command in command_list:
        assert command in str(mock_call_command.call_args_list)
        assert 'write=True' in str(mock_call_command.call_args_list)


@pytest.mark.django_db
@mock.patch('dataservices.management.commands.helpers.MarketGuidesDataIngestionCommand.should_ingestion_run')
@mock.patch('dataservices.management.commands.import_market_guides_data.call_command')
def test_import_market_guides_data_dry_run(mock_call_command, mock_should_run):
    command_list = [
        'import_uk_total_trade_data',
        'import_uk_trade_in_goods_data',
        'import_uk_trade_in_services_data',
        'import_world_economic_outlook_data',
    ]
    mock_should_run.return_value = True

    management.call_command('import_market_guides_data')

    assert mock_call_command.call_count == 4

    for command in command_list:
        assert command in str(mock_call_command.call_args_list)
        assert 'write=False' in str(mock_call_command.call_args_list)


@pytest.mark.django_db
@mock.patch('dataservices.management.commands.helpers.notifications_client')
@mock.patch('dataservices.management.commands.helpers.MarketGuidesDataIngestionCommand.should_ingestion_run')
@mock.patch('dataservices.management.commands.import_market_guides_data.call_command')
def test_import_market_guides_data_error(mock_call_command, mock_should_run, mock_error_email):
    mock_should_run.return_value = True
    mock_call_command.side_effect = Exception('oops')
    mock_error_email.return_value = mock.Mock()

    management.call_command('import_market_guides_data')

    mock_email_string = str(mock_error_email.mock_calls)
    assert mock_call_command.call_count == 4
    assert 'oops' in str(mock_call_command.side_effect)
    assert mock_error_email.call_count == 4
    assert 'area_of_error' in mock_email_string
    assert 'error_type' in mock_email_string
    assert 'error_details' in mock_email_string


@pytest.fixture()
def workspace_data():
    return {
        'schemas': 'dataflow.metadata',
        'table_name': [
            'trade__uk_goods_nsa',
        ],
        'source_data_modified_utc': [
            datetime(2023, 9, 3),
        ],
        'dataflow_swapped_tables_utc': [datetime(2023, 9, 3)],
    }


@pytest.mark.parametrize(
    'env, view_date, swap_date, expected',
    [
        ('staging', datetime(2023, 9, 12), datetime(2023, 9, 13), True),
        ('staging', datetime(2023, 9, 14), datetime(2023, 9, 13), False),
        ('production', datetime(2023, 9, 6), datetime(2023, 9, 6), False),
        ('production', datetime(2023, 9, 1), datetime(2023, 9, 2), True),
    ],
)
@mock.patch('dataservices.management.commands.helpers.MarketGuidesDataIngestionCommand.get_view_metadata')
@mock.patch('dataservices.management.commands.helpers.MarketGuidesDataIngestionCommand.get_dataflow_metadata')
@freeze_time('2023-09-14T15:21:10')
def test_helper_should_ingest_run(dataflow_mock, view_mock, env, view_date, swap_date, expected, workspace_data):
    with override_settings(APP_ENVIRONMENT=env):
        m = MarketGuidesDataIngestionCommand()
        workspace_data['dataflow_swapped_tables_utc'] = swap_date
        dataflow_mock.return_value = pd.DataFrame(workspace_data)
        view_mock.return_value = view_date.strftime('%Y-%m-%dT%H:%M:%S')
        actual = m.should_ingestion_run('UKMarketTrendsView', 'trade__uk_goods_nsa')
        assert actual == expected


@pytest.mark.django_db
def test_helper_get_view_metadata():
    result_none = MarketGuidesDataIngestionCommand().get_view_metadata('')
    assert result_none is None
    models.Metadata.objects.create(
        view_name='UKMarketTrendsView',
        description='',
        data=json.loads(
            '{"source": {"url": \"https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets\
                /uktotaltradeallcountriesseasonallyadjusted", "label": "UK total trade: all countries, seasonally \
                    adjusted", "last_release": "2022-07-27T00:00:00", "organisation": "ONS"}}'
        ),
    )
    models.Metadata.objects.create(
        view_name='TopFiveGoodsExportsByCountryView',
        description='',
        data=json.loads(
            '{"source": {"url": "https://www.ons.gov.uk/economy/nationalaccounts/balanceofpayments/datasets\
                /uktradecountrybycommodityexports", "label": "Trade in goods: country-by-commodity exports", \
                    "last_release": "2022-09-12T00:00:00", "organisation": "ONS"}}'
        ),
    )
    result = MarketGuidesDataIngestionCommand().get_view_metadata('UKMarketTrendsView')
    assert isinstance(result, str)
    assert result == '2022-07-27T00:00:00'


@override_settings(DATA_WORKSPACE_DATASETS_URL='sqlite://')
@pytest.mark.django_db
def test_helper_get_dataflow_metadata():
    m = MarketGuidesDataIngestionCommand()
    m.engine = sqlalchemy.create_engine('sqlite://')
    m.engine.execute('ATTACH DATABASE ":memory:" AS dataflow')
    meta = MetaData(schema='dataflow', quote_schema=True)
    tbl = Table(
        'metadata',
        meta,
        Column('table_name', String),
        Column('source_data_modified_utc', TIMESTAMP),
        Column('dataflow_swapped_tables_utc', TIMESTAMP),
    )
    meta.create_all(m.engine)
    m.engine.execute(
        tbl.insert().values(
            table_name='trade__uk_goods_nsa',
            source_data_modified_utc=date(2023, 1, 1),
            dataflow_swapped_tables_utc=date(2023, 1, 1),
        )
    )
    m.engine.execute(
        tbl.insert().values(
            table_name='trade__uk_goods_nsa',
            source_data_modified_utc=date(2023, 4, 1),
            dataflow_swapped_tables_utc=date(2023, 4, 1),
        )
    )
    m.engine.execute(
        tbl.insert().values(
            table_name='trade__uk_services_nsa',
            source_data_modified_utc=date(2023, 6, 1),
            dataflow_swapped_tables_utc=date(2023, 6, 1),
        )
    )
    result = m.get_dataflow_metadata('trade__uk_goods_nsa')
    expected = '2023-04-01 00:00:00.000000'
    assert result.loc[:, 'dataflow_swapped_tables_utc'][0] == expected
    assert result.loc[:, 'source_data_modified_utc'][0] == expected


@pytest.mark.django_db
def test_import_markets_countries_territories(capsys):
    management.call_command('import_markets_countries_territories', '--write')
    assert models.Market.objects.count() == 269
    # correct types and enabled status
    territory = models.Market.objects.get(name='Akrotiri')
    assert territory.type == 'Territory'
    assert territory.enabled is False
    country = models.Market.objects.get(name='Albania')
    assert country.type == 'Country'
    assert country.enabled is True
    # altered enabled status
    country.enabled = False
    territory.enabled = True
    country.save()
    territory.save()
    command_imct().check_non_default_enabled()
    captured = capsys.readouterr()
    assert captured.out == (
        'These markets do not have the default enabled status, they will require this change to be done manually!\n'
        'Finished importing markets!\n'
        'These markets do not have the default enabled status, they will require this change to be done manually!\n'
        'Albania - Change to DISABLED\n'
        'Akrotiri - Change to ENABLED\n'
    )


@pytest.mark.django_db
def test_import_markets_countries_territories_no_arg(capfd):
    management.call_command('import_markets_countries_territories')
    captured = capfd.readouterr()
    assert models.Market.objects.count() == 0
    assert captured.err == 'Must provide the --write argument. This is destructive for existing data.\n'


@pytest.mark.django_db
def test_import_countries_territories_regions():
    management.call_command('import_countries_territories_regions_dw', '--write')
    assert models.CountryTerritoryRegion.objects.all().count() == 269


@mock.patch(
    'dataservices.management.commands.import_countries_territories_regions_dw.Command.DEFAULT_FILENAME', new='abc.csv'
)
def test_import_countries_territories_regions_errors(capsys):
    management.call_command('import_countries_territories_regions_dw', '--write')
    captured = capsys.readouterr()
    assert captured[1] == "[Errno 2] No such file or directory: 'abc.csv'\n"
