import json

import pytest

from dataservices import models


@pytest.fixture(autouse=True)
def countries():
    country_uk, _ = models.Country.objects.get_or_create(iso2='GB', iso3='GBR', name='United Kingdom', iso1=826)
    country_in, _ = models.Country.objects.get_or_create(iso2='IN', iso3='IND', name='India', iso1=200)
    country_ca, _ = models.Country.objects.get_or_create(iso2='CA', iso3='CAN', name='Canada', iso1=201)
    country_cn, _ = models.Country.objects.get_or_create(iso2='CN', iso3='CHN', name='China', iso1=203)
    country_fr, _ = models.Country.objects.get_or_create(iso1='250', iso2='FR', iso3='FRA', name='France')
    country_nl, _ = models.Country.objects.get_or_create(iso1='528', iso2='NL', iso3='NLD', name='Netherlands')
    country_de, _ = models.Country.objects.get_or_create(iso2='DE', iso3='DEU', name='Germany')
    return {
        'IN': country_in,
        'GB': country_uk,
        'CA': country_ca,
        'CN': country_cn,
        'FR': country_fr,
        'NL': country_nl,
        'DE': country_de,
    }


@pytest.fixture
def internet_usage_data(countries):
    country_data = [
        models.InternetUsage(
            country=countries['GB'],
            year=2020,
            value=90.97,
        ),
        models.InternetUsage(country=countries['DE'], year=2020, value=91.97),
    ]
    yield models.InternetUsage.objects.bulk_create(country_data)


@pytest.fixture
def comtrade_report_data(countries):
    models.ComtradeReport.objects.create(
        country=countries['FR'],
        country_iso3='FRA',
        year=2020,
        commodity_code='123456',
        trade_value=90.97,
    )
    models.ComtradeReport.objects.create(
        country=countries['NL'],
        country_iso3='NLD',
        year=2020,
        commodity_code='123456',
        trade_value=91.97,
    )
    yield
    models.ComtradeReport.objects.all().delete()


@pytest.fixture
def multi_country_data(countries):
    models.EaseOfDoingBusiness.objects.create(
        country=countries['FR'],
        year=2019,
        value=12,
    )
    models.EaseOfDoingBusiness.objects.create(country=countries['NL'], year=2019, value=13)
    models.CIAFactbook.objects.create(
        country=countries['FR'],
        country_name='France',
        country_key='france',
        factbook_data={'people': {'languages': {'language': [{'name': 'French'}]}}},
    )
    models.CIAFactbook.objects.create(
        country=countries['NL'],
        country_name='Netherlands',
        country_key='netherlands',
        factbook_data={'people': {'languages': {'language': [{'name': 'Dutch'}]}}},
    )

    yield
    models.EaseOfDoingBusiness.objects.all().delete()
    models.CIAFactbook.objects.all().delete()


@pytest.fixture
def age_group_data(countries):
    count = 0
    for year in [2019, 2020]:
        for gender in ['male', 'female']:
            count += 1
            models.PopulationData.objects.create(
                country=countries['FR'],
                year=year,
                age_0_4=count,
                gender=gender,
            )
    yield
    models.PopulationData.objects.all().delete()


@pytest.fixture
def trade_barrier_data():
    with open('dataservices/tests/fixtures/trade-barrier-data.json', 'r') as f:
        return json.loads(f.read())


@pytest.fixture()
def total_trade_records(countries):
    for idx, iso2 in enumerate(['W1', 'DE', 'FR', 'CN']):
        for year in [2020, 2021]:
            for quarter in [1, 2, 3, 4]:
                models.UKTotalTradeByCountry.objects.create(
                    country=countries.get(iso2, None),
                    ons_iso_alpha_2_code=iso2,
                    year=year,
                    quarter=quarter,
                    imports=idx + 1,
                    exports=idx + 1,
                )


@pytest.fixture()
def trade_in_services_records(countries):
    records = [
        {'code': '0', 'name': 'none value', 'exports': None, 'imports': None},
        {'code': '1', 'name': 'first', 'exports': 6, 'imports': 1},
        {'code': '2', 'name': 'second', 'exports': 5, 'imports': 1},
        {'code': '3', 'name': 'third', 'exports': 4, 'imports': 1},
        {'code': '4', 'name': 'fourth', 'exports': 3, 'imports': 1},
        {'code': '5', 'name': 'fifth', 'exports': 2, 'imports': 1},
        {'code': '6', 'name': 'last', 'exports': 1, 'imports': 1},
    ]

    for iso2 in ['DE', 'FR', 'CN']:
        for year in [2020, 2021]:
            for quarter in [1, 2, 3, 4]:
                for record in records:
                    models.UKTradeInServicesByCountry.objects.create(
                        country=countries[iso2],
                        period=f'quarter/{year}-Q{quarter}',
                        period_type='quarter',
                        service_code=record['code'],
                        service_name=record['name'],
                        imports=record['imports'],
                        exports=record['exports'],
                    )
            for record in records:
                models.UKTradeInServicesByCountry.objects.create(
                    country=countries[iso2],
                    period=f'year/{year}',
                    period_type='year',
                    service_code=record['code'],
                    service_name=record['name'],
                    imports=record['imports'],
                    exports=record['exports'],
                )


@pytest.fixture()
def trade_in_goods_records(countries):
    for idx, iso2 in enumerate(['DE', 'FR', 'CN']):
        records = [
            {'code': '0', 'name': 'none value', 'exports': None, 'imports': None},
            {'code': '1', 'name': 'first', 'exports': 6, 'imports': 1},
            {'code': '2', 'name': 'second', 'exports': 5, 'imports': 1},
            {'code': '3', 'name': 'third', 'exports': 4, 'imports': 1},
            {'code': '4', 'name': 'fourth', 'exports': 3, 'imports': 1},
            {'code': '5', 'name': 'fifth', 'exports': 2, 'imports': 1},
            {'code': '6', 'name': 'last', 'exports': 1, 'imports': 1},
        ]
        for year in [2020, 2021]:
            for quarter in [1, 2, 3, 4]:
                for record in records:
                    models.UKTradeInGoodsByCountry.objects.create(
                        country=countries[iso2],
                        year=year,
                        quarter=quarter,
                        commodity_code=record['code'],
                        commodity_name=record['name'],
                        imports=record['imports'],
                        exports=record['exports'],
                    )


@pytest.fixture()
def world_economic_outlook_records(countries):
    for idx, (iso2, estimates_after) in enumerate({'GB': 2019, 'DE': 2020, 'CN': 2021}.items(), 1):
        for code, descriptor in {'NGDPDPC': 'GDPPC, current prices', 'NGDP_RPCH': 'GDP, constant prices'}.items():
            for year in range(2018, 2022):
                models.WorldEconomicOutlookByCountry.objects.create(
                    country=countries[iso2],
                    subject_code=code,
                    subject_descriptor=descriptor,
                    units='',
                    scale='',
                    year=year,
                    value=idx,
                    estimates_start_after=estimates_after,
                )


@pytest.fixture()
def metadata_last_release_records():
    data = {
        'TopFiveGoodsExportsByCountryView': '30 June 2020',
        'TopFiveServicesExportsByCountryView': '30 June 2021',
        'UKMarketTrendsView': '30 June 2022',
        'UKTradeHighlightsView': '30 June 2022',
    }
    for view_name, last_release in data.items():
        models.Metadata.objects.create(view_name=view_name, data={'last_release': last_release})
