import json

import pytest

from dataservices import models


@pytest.fixture
def internet_usage_data():
    country_data = [
        models.InternetUsage(
            country_code='GBR',
            country_name='United Kingdom',
            year=2020,
            value=90.97,
        ),
        models.InternetUsage(country_code='DEU', country_name='Germany', year=2020, value=91.97),
    ]
    yield models.InternetUsage.objects.bulk_create(country_data)
    models.InternetUsage.objects.all().delete()


def countries_data():
    return {
        'FR': models.Country.objects.create(iso1='1', iso2='FR', iso3='FRA', name='France'),
        'NL': models.Country.objects.create(iso1='2', iso2='NL', iso3='NLD', name='Netherlands'),
    }


@pytest.fixture
def comtrade_report_data():
    countries = countries_data()
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
    models.Country.objects.all().delete()


@pytest.fixture
def multi_country_data():
    countries = countries_data()
    models.EaseOfDoingBusiness.objects.create(
        country=countries['FR'],
        country_name='France',
        country_code='FR',
        year_2019=12,
    )
    models.EaseOfDoingBusiness.objects.create(
        country=countries['NL'],
        country_code='NL',
        country_name='Netherlands',
        year_2019=13,
    )
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
    models.Country.objects.all().delete()


@pytest.fixture
def age_group_data():
    countries = countries_data()
    models.PopulationData.objects.create(
        country=countries['FR'],
        year=2019,
        age_0_4=1,
        gender='male',
    )
    models.PopulationData.objects.create(
        country=countries['FR'],
        year=2019,
        age_0_4=2,
        gender='female',
    )
    models.PopulationData.objects.create(
        country=countries['FR'],
        year=2020,
        age_0_4=3,
        gender='male',
    )
    models.PopulationData.objects.create(
        country=countries['FR'],
        year=2020,
        age_0_4=4,
        gender='female',
    )
    yield
    models.PopulationData.objects.all().delete()
    models.Country.objects.all().delete()


@pytest.fixture
def trade_barrier_data():
    with open('dataservices/tests/fixtures/trade-barrier-data.json', 'r') as f:
        return json.loads(f.read())
