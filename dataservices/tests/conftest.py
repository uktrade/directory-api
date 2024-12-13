import gzip
import io
import json
from datetime import datetime

import pytest
from botocore.response import StreamingBody

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
    yield
    models.UKTotalTradeByCountry.objects.all().delete()


@pytest.fixture()
def trade_in_services_records(countries):
    records = [
        {'code': '0', 'name': 'null value', 'exports': None, 'imports': None},
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
    yield
    models.UKTradeInServicesByCountry.objects.all().delete()


@pytest.fixture()
def trade_in_goods_records(countries):
    for idx, iso2 in enumerate(['DE', 'FR', 'CN']):
        records = [
            {'code': '0', 'name': 'null value', 'exports': None, 'imports': None},
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
    yield
    models.UKTradeInGoodsByCountry.objects.all().delete()


@pytest.fixture()
def world_economic_outlook_records(countries):
    for idx, (iso2, estimates_after) in enumerate({'GB': 2019, 'DE': 2020, 'CN': 2021}.items(), 1):
        for code, descriptor in {
            'MKT_POS': 'Market size rankings',
            'NGDPDPC': 'GDPPC, current prices',
            'NGDP_RPCH': 'GDP, constant prices',
        }.items():
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
    yield
    models.WorldEconomicOutlookByCountry.objects.all().delete()


@pytest.fixture()
def metadata_source_records():
    data = {
        'TopFiveGoodsExportsByCountryView': {
            'source': {'organisation': 'ONS', 'label': 'goods exports', 'last_release': '30 June 2020'}
        },
        'TopFiveServicesExportsByCountryView': {
            'source': {'organisation': 'ONS', 'label': 'services exports', 'last_release': '30 June 2021'}
        },
        'UKMarketTrendsView': {
            'source': {'organisation': 'ONS', 'label': 'total exports', 'last_release': '30 June 2022'}
        },
        'UKTradeHighlightsView': {
            'source': {'organisation': 'ONS', 'label': 'total exports', 'last_release': '30 June 2022'}
        },
    }
    for view_name, metadata in data.items():
        models.Metadata.objects.create(view_name=view_name, data=metadata)
    yield
    models.Metadata.objects.all().delete()


@pytest.fixture()
def uk_trade_agreements_records(countries):
    fta_records = [
        ('IN', 'FTA with India'),
        ('CN', 'FTA with China'),
        ('CA', 'FTA with Canada'),
    ]

    for iso2, name in fta_records:
        models.UKFreeTradeAgreement.objects.create(country=countries[iso2], name=name)
    yield
    models.UKFreeTradeAgreement.objects.all().delete()


@pytest.fixture()
def business_cluster_information_data():
    records = [
        {
            'geo_description': 'England',
            'geo_code': 'E92000001',
            'sic_code': '95110',
            'sic_description': 'Repair of computers and peripheral equipment',
            'total_business_count': 4020,
            'business_count_release_year': 2023,
            'total_employee_count': 31000,
            'employee_count_release_year': 2023,
            'dbt_full_sector_name': 'Technology and smart cities : Hardware',
            'dbt_sector_name': 'Technology and smart cities',
        },
        {
            'geo_description': 'Northern Ireland',
            'geo_code': 'N92000002',
            'sic_code': '95110',
            'sic_description': 'Repair of computers and peripheral equipment',
            'total_business_count': 55,
            'business_count_release_year': 2023,
            'total_employee_count': None,
            'employee_count_release_year': None,
            'dbt_full_sector_name': 'Technology and smart cities : Hardware',
            'dbt_sector_name': 'Technology and smart cities',
        },
        {
            'geo_description': 'England',
            'geo_code': 'E92000001',
            'sic_code': '94990',
            'sic_description': 'Activities of other membership organisations nec',
            'total_business_count': 5700,
            'business_count_release_year': 2023,
            'total_employee_count': 99000,
            'employee_count_release_year': 2023,
            'dbt_full_sector_name': 'Financial and professional services',
            'dbt_sector_name': 'Financial and professional services',
        },
        {
            'geo_description': 'Yorkshire and The Humber',
            'geo_code': 'E12000003',
            'sic_code': 'L',
            'sic_description': 'Real estate activities',
            'total_business_count': 7625,
            'business_count_release_year': 2022,
            'total_employee_count': 33000,
            'employee_count_release_year': 2021,
            'dbt_full_sector_name': None,
            'dbt_sector_name': None,
        },
        {
            'geo_description': 'London',
            'geo_code': 'E12000007',
            'sic_code': '82',
            'sic_description': 'Office administrative, office support and other business support activities',
            'total_business_count': 26110,
            'business_count_release_year': 2023,
            'total_employee_count': 147000,
            'employee_count_release_year': 2023,
            'dbt_full_sector_name': None,
            'dbt_sector_name': None,
        },
    ]

    for record in records:
        models.EYBBusinessClusterInformation.objects.create(**record)
    yield
    models.EYBBusinessClusterInformation.objects.all().delete()


@pytest.fixture
def sector_reference_dataset_data():
    yield [
        '{"id": 3, "field_04": "Advanced engineering",  "full_sector_name": "Advanced engineering : Metallurgical process plant"}\n',  # noqa: E501
        '{"id": 4, "field_04": "Advanced engineering",  "full_sector_name": "Advanced engineering : Metals, minerals and materials"}\n',  # noqa: E501
        '{"id": 38, "field_04": "Automotive", "full_sector_name": "Automotive"}\n',  # noqa: E501
    ]


@pytest.fixture
def ref_sic_codes_mapping_data():
    yield [
        '{"id": 1, "sic_code": 1110, "mapping_id": "SIC-SEC-106", "updated_date": "2021-08-19T10:05:34.680837+00:00", "sic_description": "Growing of cereals (except rice), leguminous crops and oil seeds", "dit_sector_list_id": 21}\n',  # noqa: E501
        '{"id": 2, "sic_code": 1120, "mapping_id": "SIC-SEC-107", "updated_date": "2021-08-19T10:05:34.689149+00:00", "sic_description": "Growing of rice", "dit_sector_list_id": 21}\n',  # noqa: E501
        '{"id": 3, "sic_code": 1130, "mapping_id": "SIC-SEC-129", "updated_date": "2021-08-19T10:05:34.696666+00:00", "sic_description": "Growing of vegetables and melons, roots and tubers", "dit_sector_list_id": 31}\n',  # noqa: E501
    ]


@pytest.fixture
def uk_business_employee_counts_data():
    yield [
        {
            "geo_code": "K02000002",
            "sic_code": "01",
            "geo_description": "United Kingdom",
            "sic_description": "Crop and animal production, hunting and related service activities",
            "total_business_count": 132540,
            "total_employee_count": None,
            "business_count_release_year": 2023,
            "employee_count_release_year": None,
            "dbt_full_sector_name": "Metallurgical process plant",
            "dbt_sector_name": "Advanced engineering",
        },  # noqa: E501
        {
            "geo_code": "K02000003",
            "sic_code": "03",
            "geo_description": "United Kingdom",
            "sic_description": "Fishing and aquaculture",
            "total_business_count": 4070,
            "total_employee_count": None,
            "business_count_release_year": 2023,
            "employee_count_release_year": None,
            "dbt_full_sector_name": "Metallurgical process plant",
            "dbt_sector_name": "Advanced engineering",
        },  # noqa: E501
        {
            "geo_code": "K02000004",
            "sic_code": "03",
            "geo_description": "United Kingdom",
            "sic_description": "Fishing and aquaculture",
            "total_business_count": 4070,
            "total_employee_count": None,
            "business_count_release_year": 2023,
            "employee_count_release_year": None,
            "dbt_full_sector_name": "Automotive",
            "dbt_sector_name": "Automotive",
        },  # noqa: E501
    ]


@pytest.fixture
def uk_business_employee_counts_str_data(uk_business_employee_counts_data):

    data = []
    for line in uk_business_employee_counts_data:
        line = json.dumps(line)
        data.append(line)
    yield data


@pytest.fixture
def eyb_salary_s3_data():
    yield [
        '{"id": "1", "code": 1121, "year": 2021, "region": "East", "created": "2024-06-04T20:04:59", "modified": "2024-06-04T20:04:59", "vertical": "Food and Drink", "color_tag": null, "occupation": "Production managers and directors in manufacturing", "mean_salary": "55763", "median_salary": "43137", "professional_level": "Director/Executive", "compliance_asset_id": null, "annual_percantage_change": null, "annual_percentage_change": null, "number_of_jobs_thousands": null}\n',  # noqa: E501
        '{"id": "2", "code": 1131, "year": 2021, "region": "East", "created": "2024-06-04T20:04:59", "modified": "2024-06-04T20:04:59", "vertical": "Finance and Professional Services", "color_tag": null, "occupation": "Financial managers and directors", "mean_salary": "56319", "median_salary": "47508", "professional_level": "Director/Executive", "compliance_asset_id": null, "annual_percantage_change": null, "annual_percentage_change": null, "number_of_jobs_thousands": null}\n',  # noqa: E501
        '{"id": "3", "code": 1132, "year": 2021, "region": "East", "created": "2024-06-04T20:04:59", "modified": "2024-06-04T20:04:59", "vertical": "Creative Industries", "color_tag": null, "occupation": "Marketing, sales and advertising directors", "mean_salary": "76034", "median_salary": "63162", "professional_level": "Director/Executive", "compliance_asset_id": null, "annual_percantage_change": null, "annual_percentage_change": null, "number_of_jobs_thousands": null}\n',  # noqa: E501
    ]


@pytest.fixture
def eyb_rent_s3_data():
    yield [
        '{"id": "1", "region": "United Kingdom", "created": "2024-05-30T11:14:33", "modified": "2024-05-30T11:14:33", "vertical": "Industrial", "color_tag": null, "square_feet": 340000, "release_year": 2023, "sub_vertical": "Large Warehouses", "gbp_per_month": 340321.96969697, "compliance_asset_id": null, "gbp_per_square_foot_per_month": 1.00094696969697}\n',  # noqa: E501
        '{"id": "2", "region": "East", "created": "2024-05-30T11:14:33", "modified": "2024-05-30T11:14:33", "vertical": "Industrial", "color_tag": null, "square_feet": 340000, "release_year": 2023, "sub_vertical": "Large Warehouses", "gbp_per_month": 566666.666666667, "compliance_asset_id": null, "gbp_per_square_foot_per_month": 1.66666666666667}\n',  # noqa: E501
        '{"id": "3", "region": "East Midlands", "created": "2024-05-30T11:14:33", "modified": "2024-05-30T11:14:33", "vertical": "Industrial", "color_tag": null, "square_feet": 340000, "release_year": 2023, "sub_vertical": "Large Warehouses", "gbp_per_month": 255000.0, "compliance_asset_id": null, "gbp_per_square_foot_per_month": 0.75}\n',  # noqa: E501
    ]


@pytest.fixture
def eyb_salary_data():
    records = [
        {
            "id": 25550,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 23469,
            "mean_salary": 25541,
            "dataset_year": 2022,
            "occupation": "Sales supervisors - retail and wholesale",
            "soc_code": 7132,
        },
        {
            "id": 27355,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 21183,
            "mean_salary": 22380,
            "dataset_year": 2023,
            "occupation": "Sales supervisors - retail and wholesale",
            "soc_code": 7132,
        },
        {
            "id": 24107,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 23020,
            "mean_salary": 24080,
            "dataset_year": 2021,
            "occupation": "Sales supervisors - retail and wholesale",
            "soc_code": 7132,
        },
        {
            "id": 27297,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 22988,
            "mean_salary": 23821,
            "dataset_year": 2023,
            "occupation": "Shopkeepers and Sales Supervisors",
            "soc_code": 7130,
        },
        {
            "id": 25548,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 31193,
            "mean_salary": 37953,
            "dataset_year": 2022,
            "occupation": "Sales Related Occupations N.E.C.",
            "soc_code": 7129,
        },
        {
            "id": 25546,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 21024,
            "mean_salary": 21857,
            "dataset_year": 2022,
            "occupation": "Market And Street Traders And Assistants",
            "soc_code": 7124,
        },
        {
            "id": 24100,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 21225,
            "mean_salary": 23164,
            "dataset_year": 2021,
            "occupation": "Debt, rent and other cash collectors",
            "soc_code": 7122,
        },
        {
            "id": 24098,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 24397,
            "mean_salary": 26057,
            "dataset_year": 2021,
            "occupation": "Vehicle and parts salespersons and advisers",
            "soc_code": 7115,
        },
        {
            "id": 27346,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 16135,
            "mean_salary": 15587,
            "dataset_year": 2023,
            "occupation": "Pharmacy and optical dispensing assistants",
            "soc_code": 7114,
        },
        {
            "id": 24097,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 16022,
            "mean_salary": 15139,
            "dataset_year": 2021,
            "occupation": "Pharmacy and optical dispensing assistants",
            "soc_code": 7114,
        },
        {
            "id": 24095,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 13296,
            "mean_salary": 13006,
            "dataset_year": 2021,
            "occupation": "Retail cashiers and check-out operators",
            "soc_code": 7112,
        },
        {
            "id": 27343,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 12966,
            "mean_salary": 14488,
            "dataset_year": 2023,
            "occupation": "Sales And Retail Assistants",
            "soc_code": 7111,
        },
        {
            "id": 24094,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 13236,
            "mean_salary": 15452,
            "dataset_year": 2021,
            "occupation": "Sales and retail assistants",
            "soc_code": 7111,
        },
        {
            "id": 27295,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 13486,
            "mean_salary": 15736,
            "dataset_year": 2023,
            "occupation": "Sales Assistants and Retail Cashiers",
            "soc_code": 7110,
        },
        {
            "id": 25508,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Entry-level",
            "median_salary": 27541,
            "mean_salary": 25444,
            "dataset_year": 2022,
            "occupation": "Merchandisers",
            "soc_code": 3553,
        },
        {
            "id": 25448,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Middle/Senior Management",
            "median_salary": 13857,
            "mean_salary": 16662,
            "dataset_year": 2022,
            "occupation": "Hairdressing And Beauty Salon Managers And Proprietors",
            "soc_code": 1253,
        },
        {
            "id": 24003,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Middle/Senior Management",
            "median_salary": 25001,
            "mean_salary": 23550,
            "dataset_year": 2021,
            "occupation": "Hairdressing and beauty salon managers and proprietors",
            "soc_code": 1253,
        },
        {
            "id": 27241,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Director/Executive",
            "median_salary": 34503,
            "mean_salary": 45565,
            "dataset_year": 2023,
            "occupation": "Managers and Directors in Retail and Wholesale",
            "soc_code": 1150,
        },
        {
            "id": 23998,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Director/Executive",
            "median_salary": 31613,
            "mean_salary": 41707,
            "dataset_year": 2021,
            "occupation": "Managers and directors in retail and wholesale",
            "soc_code": 1150,
        },
        {
            "id": 27340,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Director/Executive",
            "median_salary": 31594,
            "mean_salary": 36704,
            "dataset_year": 2023,
            "occupation": "Managers And Directors In Retail And Wholesale",
            "soc_code": 1150,
        },
        {
            "id": 25443,
            "geo_description": "London",
            "vertical": "Consumer and Retail",
            "professional_level": "Director/Executive",
            "median_salary": 29753,
            "mean_salary": 31626,
            "dataset_year": 2022,
            "occupation": "Managers And Directors In Retail And Wholesale",
            "soc_code": 1150,
        },
    ]

    for record in records:
        models.EYBSalaryData.objects.create(**record)
    yield records
    models.EYBSalaryData.objects.all().delete()


@pytest.fixture
def eyb_rent_data():
    records = [
        {
            "id": 1,
            "geo_description": "London",
            "vertical": "Industrial",
            "sub_vertical": "Large Warehouses",
            "gbp_per_square_foot_per_month": 2.292,
            "square_feet": 340000.000,
            "gbp_per_month": 779166.667,
            "dataset_year": 2023,
        },
        {
            "id": 2,
            "geo_description": "London",
            "vertical": "Industrial",
            "sub_vertical": "Small Warehouses",
            "gbp_per_square_foot_per_month": 1.863,
            "square_feet": 5000.000,
            "gbp_per_month": 9317.130,
            "dataset_year": 2023,
        },
        {
            "id": 3,
            "geo_description": "London",
            "vertical": "Retail",
            "sub_vertical": "High Street Retail",
            "gbp_per_square_foot_per_month": 74.722,
            "square_feet": 2195.000,
            "gbp_per_month": 164015.278,
            "dataset_year": 2023,
        },
        {
            "id": 4,
            "geo_description": "London",
            "vertical": "Retail",
            "sub_vertical": "Prime shopping centre",
            "gbp_per_square_foot_per_month": 14.443,
            "square_feet": 2195.000,
            "gbp_per_month": 31702.791,
            "dataset_year": 2023,
        },
        {
            "id": 5,
            "geo_description": "London",
            "vertical": "Office",
            "sub_vertical": "Work Office",
            "gbp_per_square_foot_per_month": 8.684,
            "square_feet": 16671.000,
            "gbp_per_month": 144770.269,
            "dataset_year": 2023,
        },
    ]

    for record in records:
        models.EYBCommercialPropertyRent.objects.create(**record)
    yield records
    models.EYBCommercialPropertyRent.objects.all().delete()


@pytest.fixture
def gva_bandings():
    records = [
        {
            "id": 1,
            "full_sector_name": "Aerospace",
            "value_band_a_minimum": 10000,
            "value_band_b_minimum": 1000,
            "value_band_c_minimum": 100,
            "value_band_d_minimum": 10,
            "value_band_e_minimum": 1,
            "start_date": "2020-04-01",
            "end_date": "2021-03-31",
            "sector_classification_value_band": "classification band",
            "sector_classification_gva_multiplier": "classification band",
        },
        {
            "id": 2,
            "full_sector_name": "Aerospace",
            "value_band_a_minimum": 20000,
            "value_band_b_minimum": 2000,
            "value_band_c_minimum": 200,
            "value_band_d_minimum": 20,
            "value_band_e_minimum": 2,
            "start_date": "2024-04-01",
            "end_date": "2025-03-31",
            "sector_classification_value_band": "classification band",
            "sector_classification_gva_multiplier": "classification band",
        },
        {
            "id": 3,
            "full_sector_name": "Aerospace",
            "value_band_a_minimum": 30000,
            "value_band_b_minimum": 3000,
            "value_band_c_minimum": 300,
            "value_band_d_minimum": 30,
            "value_band_e_minimum": 3,
            "start_date": "2022-04-01",
            "end_date": "2023-03-31",
            "sector_classification_value_band": "classification band",
            "sector_classification_gva_multiplier": "classification band",
        },
        {
            "id": 4,
            "full_sector_name": "Technology and smart cities : Software : Blockchain",
            "value_band_a_minimum": 40000,
            "value_band_b_minimum": 4000,
            "value_band_c_minimum": 400,
            "value_band_d_minimum": 40,
            "value_band_e_minimum": 4,
            "start_date": "2020-04-01",
            "end_date": "2021-03-31",
            "sector_classification_value_band": "classification band",
            "sector_classification_gva_multiplier": "classification band",
        },
        {
            "id": 5,
            "full_sector_name": "Technology and smart cities : Software : Blockchain",
            "value_band_a_minimum": 50000,
            "value_band_b_minimum": 5000,
            "value_band_c_minimum": 500,
            "value_band_d_minimum": 50,
            "value_band_e_minimum": 5,
            "start_date": "2021-04-01",
            "end_date": "2022-03-31",
            "sector_classification_value_band": "classification band",
            "sector_classification_gva_multiplier": "classification band",
        },
        {
            "id": 6,
            "full_sector_name": "Technology and smart cities : Software : Blockchain",
            "value_band_a_minimum": 60000,
            "value_band_b_minimum": 6000,
            "value_band_c_minimum": 600,
            "value_band_d_minimum": 60,
            "value_band_e_minimum": 6,
            "start_date": "2023-04-01",
            "end_date": "2025-03-31",
            "sector_classification_value_band": "classification band",
            "sector_classification_gva_multiplier": "classification band",
        },
    ]

    for record in records:
        models.SectorGVAValueBand.objects.create(**record)
    yield
    models.SectorGVAValueBand.objects.all().delete()


@pytest.fixture
def countries_territories_regions():
    records = [
        {
            "id": 1,
            "created": "2024-10-28T10:41:50.386827Z",
            "modified": "2024-10-28T10:41:50.386829Z",
            "reference_id": "CTHMTC00086",
            "name": "France",
            "type": "Country",
            "iso1_code": "250",
            "iso2_code": "FR",
            "iso3_code": "FRA",
            "overseas_region": "Europe",
            "start_date": None,
            "end_date": None,
        },
        {
            "id": 2,
            "created": "2024-10-28T10:41:50.388641Z",
            "modified": "2024-10-28T10:41:50.388644Z",
            "reference_id": "CTHMTC00212",
            "name": "Saudi Arabia",
            "type": "Country",
            "iso1_code": "682",
            "iso2_code": "SA",
            "iso3_code": "SAU",
            "overseas_region": "Middle East, Afghanistan and Pakistan",
            "start_date": None,
            "end_date": None,
        },
        {
            "id": 3,
            "created": "2024-10-28T10:41:50.387952Z",
            "modified": "2024-10-28T10:41:50.387955Z",
            "reference_id": "CTHMTC00174",
            "name": "New Zealand",
            "type": "Country",
            "iso1_code": "554",
            "iso2_code": "NZ",
            "iso3_code": "NZL",
            "overseas_region": "Asia Pacific",
            "start_date": None,
            "end_date": None,
        },
    ]

    for record in records:
        models.CountryTerritoryRegion.objects.create(**record)
    yield
    models.CountryTerritoryRegion.objects.all().delete()


@pytest.fixture
def get_s3_file_data(request):
    json_data = request.param
    body_encoded = json.dumps(json_data).encode()
    gzipped_body = gzip.compress(body_encoded)
    body = StreamingBody(io.BytesIO(gzipped_body), len(gzipped_body))
    data = {
        'ResponseMetadata': {
            'RequestId': '84F2PA3B0RC5J6WX',
            'HostId': 'MJ7MDrEA/CRqVwA3DlKCCjKxXKDk31ZozEsxTJM4MzwOeleZOeI9d5/p/TT/yFLZiUn2GiIixJE=',
            'HTTPStatusCode': 200,
            'HTTPHeaders': {
                'x-amz-id-2': 'MJ7MDrEA/CRqVwA3DlKCCjKxXKDk31ZozEsxTJM4MZOeI9d5/p/TT/yFLZiUn2GiIixJE=',
                'x-amz-request-id': '84F2PA3B0RC5J6WX',
                'date': 'Wed, 28 Aug 2024 14:42:25 GMT',
                'last-modified': 'Wed, 28 Aug 2024 08:27:43 GMT',
                'etag': '"3146b7a34b9f97ee85cbf81c725e8862-2"',
                'x-amz-server-side-encryption': 'AES256',
                'accept-ranges': 'bytes',
                'content-type': 'binary/octet-stream',
                'server': 'AmazonS3',
                'content-length': '104182994',
            },
            'RetryAttempts': 0,
        },
        'AcceptRanges': 'bytes',
        'LastModified': datetime(2024, 8, 28, 8, 27, 43),
        'ContentLength': 2,
        'ETag': '"3146b7a34b9f97ee85cbf81c725e8862-2"',
        'ContentType': 'binary/octet-stream',
        'ServerSideEncryption': 'AES256',
        'Metadata': {},
        'Body': body,
    }
    yield data


@pytest.fixture
def get_s3_data_transfer_data():
    data = [
        {
            'ResponseMetadata': {
                'RequestId': 'E6VQET72ZW9TWAEA',
                'HostId': 'bGXaG1MHY2XchguWpfrHTlL+Y1VjERk3t735RcWKuh2Lq7Ybm3xz1FdXzz5U16a76mQcqAukg==',
                'HTTPStatusCode': 200,
                'HTTPHeaders': {
                    'x-amz-id-2': 'bGXaG1MHY2XchguWpfrnoS6oWApoeTfnHTlL+g==',
                    'x-amz-request-id': 'E6VQET72ZW9TWAEA',
                    'date': 'Wed, 28 Aug 2024 14:26:58 GMT',
                    'x-amz-bucket-region': 'eu-west-2',
                    'content-type': 'application/xml',
                    'transfer-encoding': 'chunked',
                    'server': 'AmazonS3',
                },
                'RetryAttempts': 0,
            },
            'IsTruncated': False,
            'Marker': '',
            'Contents': [
                {
                    'Key': '20240818T000000.jsonl.gz',
                    'LastModified': datetime(2024, 8, 28, 8, 27, 43),
                    'ETag': '"3146b7a34b9f97ee85cbf81c725e8862-2"',
                    'Size': 2,
                    'StorageClass': 'STANDARD',
                    'Owner': {'ID': '3f810126f6b9e06a7bd7ee566fc58a4b80bec947dab08ea4bcaee9f0b26e9380'},
                },
            ],
            'Name': 'paas-s3-broker-prod-lon-4ba96c09-0310-4f05-9eac-b0ff2f69357a',
            'Prefix': 'data-flow/exports/production/dataset',
            'MaxKeys': 1000,
            'EncodingType': 'url',
        },
        {
            'ResponseMetadata': {
                'RequestId': 'E6VQET72ZW9TWAEA',
                'HostId': 'bGXaG1MHY2XchguWpfrHTlL+Y1VjERk3t735RcWKuh2Lq7Ybm3xz1FdXzz5U16a76mQcqAukg==',
                'HTTPStatusCode': 200,
                'HTTPHeaders': {
                    'x-amz-id-2': 'bGXaG1MHY2XchguWpfrnoS6oWApoeTfnHTlL+g==',
                    'x-amz-request-id': 'E6VQET72ZW9TWAEA',
                    'date': 'Wed, 28 Aug 2024 14:26:58 GMT',
                    'x-amz-bucket-region': 'eu-west-2',
                    'content-type': 'application/xml',
                    'transfer-encoding': 'chunked',
                    'server': 'AmazonS3',
                },
                'RetryAttempts': 0,
            },
            'IsTruncated': False,
            'Marker': '',
            'Contents': [
                {
                    'Key': '20240818T000000.jsonl.gz',
                    'LastModified': datetime(2024, 8, 29, 8, 27, 43),
                    'ETag': '"3146b7a34b9f97ee85cbf81c725e8862-2"',
                    'Size': 2,
                    'StorageClass': 'STANDARD',
                    'Owner': {'ID': '3f810126f6b9e06a7bd7ee566fc58a4b80bec947dab08ea4bcaee9f0b26e9380'},
                }
            ],
            'Name': 'paas-s3-broker-prod-lon-4ba96c09-0310-4f05-9eac-b0ff2f69357a',
            'Prefix': 'data-flow/exports/production/dataset',
            'MaxKeys': 1000,
            'EncodingType': 'url',
        },
    ]
    yield data


@pytest.fixture
def dbtsector_data():
    yield [
        '{"id": 3, "field_01": "SL0003", "field_02": "", "field_03": "Technology and Advanced Manufacturing", "field_04": "Advanced engineering", "field_05": "Metallurgical process plant", "field_06": "", "field_07": "", "updated_date": "2021-08-19T07:12:32.744274+00:00", "full_sector_name": "Advanced engineering : Metallurgical process plant", "sector_cluster__april_2023": "Sustainability and Infrastructure"}\n',  # noqa: E501
    ]


@pytest.fixture
def sectors_gva_value_bands_data():
    yield [
        '{"id": 382, "end_date": "2022-03-31", "start_date": "2021-04-01", "gva_grouping": "Transport equipment", "updated_date": "2022-06-16T12:59:44.743973+00:00", "gva_multiplier": 0.209650945, "full_sector_name": "Automotive", "value_band_a_minimum": 13500000, "value_band_b_minimum": 5057796, "value_band_c_minimum": 1530000, "value_band_d_minimum": 397422, "value_band_e_minimum": 10000, "sector_gva_and_value_band_id": 382, "sector_classification_value_band": "Capital intensive", "sector_classification_gva_multiplier": "Capital intensive"}\n',  # noqa: E501
    ]


@pytest.fixture
def investment_opportunities_data():
    yield [
        '{"id": 2, "launched": true, "location": "Doncaster", "net_zero": true, "sub_sector": "Infrastructure", "description": "An opportunity for international investors supplying into the rolling stock industry.", "levelling_up": true, "updated_date": "2024-07-10T11:39:16.682655+00:00", "sector_cluster": "Sustainability and Infrastructure", "nomination_round": 1, "opportunity_type": "High potential opportunity", "opportunity_title": "Rail", "investment_opportunity_code": "INVESTMENT_OPPORTUNITY_002", "science_technology_superpower": false}\n',  # noqa: E501
    ]


@pytest.fixture
def postcode_data():
    yield [
        '{"id": 2656, "ccg": "S03000012", "ced": "S99999999", "eer": "S15000001", "imd": 3888, "lat": 57.148232, "pcd": "AB101AA", "pct": "S03000012", "pfa": "S23000009", "rgn": "S99999999", "stp": "S99999999", "ctry": "S92000003", "lep1": "S99999999", "lep2": "S99999999", "long": -2.096648, "nuts": "S30000026", "oa01": "S00000036", "oa11": "S00090540", "park": "S99999999", "pcd2": "AB10 1AA", "pcds": "AB10 1AA", "pcon": "S14000001", "ttwa": "S22000047", "wz11": "S34000028", "bua11": "S99999999", "nhser": "S99999999", "oac01": "2A1", "oac11": "2B1", "oscty": "S99999999", "streg": 0, "calncv": "S99999999", "dointr": "2011-09-01", "doterm": "2016-10-01", "lsoa01": "S01000125", "lsoa11": "S01006646", "msoa01": "S02000024", "msoa11": "S02001261", "oslaua": "S12000033", "osward": "S13002842", "parish": "S99999999", "teclec": "S09000001", "buasd11": "S99999999", "casward": "01C28", "ru11ind": "1", "ur01ind": "1", "oseast1m": "394251", "osgrdind": 1, "oshlthau": "S08000020", "osnrth1m": "0806376", "usertype": 1, "statsward": "99ZZ00", "region_name": "Scotland", "pcd_normalised": "AB101AA", "publication_date": "2022-11-01", "local_authority_district_name": "Aberdeen City", "parliamentary_constituency_name": "Aberdeen North", "lep1_local_enterprise_partnership_name": null, "lep2_local_enterprise_partnership_name": null}\n',  # noqa: E501
        '{"id": 2657, "ccg": "S03000012", "ced": "S99999999", "eer": "S15000001", "imd": 3888, "lat": 57.149606, "pcd": "AB101AB", "pct": "S03000012", "pfa": "S23000009", "rgn": "S99999999", "stp": "S99999999", "ctry": "S92000003", "lep1": "S99999999", "lep2": "S99999999", "long": -2.096916, "nuts": "S30000026", "oa01": "S00000036", "oa11": "S00090540", "park": "S99999999", "pcd2": "AB10 1AB", "pcds": "AB10 1AB", "pcon": "S14000001", "ttwa": "S22000047", "wz11": "S34000028", "bua11": "S99999999", "nhser": "S99999999", "oac01": "2A1", "oac11": "2B1", "oscty": "S99999999", "streg": 0, "calncv": "S99999999", "dointr": "2011-06-01", "doterm": null, "lsoa01": "S01000125", "lsoa11": "S01006646", "msoa01": "S02000024", "msoa11": "S02001261", "oslaua": "S12000033", "osward": "S13002842", "parish": "S99999999", "teclec": "S09000001", "buasd11": "S99999999", "casward": "01C28", "ru11ind": "1", "ur01ind": "1", "oseast1m": "394235", "osgrdind": 1, "oshlthau": "S08000020", "osnrth1m": "0806529", "usertype": 1, "statsward": "99ZZ00", "region_name": "Scotland", "pcd_normalised": "AB101AB", "publication_date": "2022-11-01", "local_authority_district_name": "Aberdeen City", "parliamentary_constituency_name": "Aberdeen North", "lep1_local_enterprise_partnership_name": null, "lep2_local_enterprise_partnership_name": null}\n',  # noqa: E501
        '{"id": 2658, "ccg": "S03000012", "ced": "S99999999", "eer": "S15000001", "imd": 3888, "lat": 57.148125, "pcd": "AB101AD", "pct": "S03000012", "pfa": "S23000009", "rgn": "S99999999", "stp": "S99999999", "ctry": "S92000003", "lep1": "S99999999", "lep2": "S99999999", "long": -2.09554, "nuts": "S30000026", "oa01": "S00000036", "oa11": "S00090540", "park": "S99999999", "pcd2": "AB10 1AD", "pcds": "AB10 1AD", "pcon": "S14000001", "ttwa": "S22000047", "wz11": "S34000028", "bua11": "S99999999", "nhser": "S99999999", "oac01": "2A1", "oac11": "2B1", "oscty": "S99999999", "streg": 0, "calncv": "S99999999", "dointr": "1996-06-01", "doterm": "2000-09-01", "lsoa01": "S01000125", "lsoa11": "S01006646", "msoa01": "S02000024", "msoa11": "S02001261", "oslaua": "S12000033", "osward": "S13002842", "parish": "S99999999", "teclec": "S09000001", "buasd11": "S99999999", "casward": "01C28", "ru11ind": "1", "ur01ind": "1", "oseast1m": "394318", "osgrdind": 1, "oshlthau": "S08000020", "osnrth1m": "0806364", "usertype": 1, "statsward": "99ZZ00", "region_name": "Scotland", "pcd_normalised": "AB101AD", "publication_date": "2022-11-01", "local_authority_district_name": "Aberdeen City", "parliamentary_constituency_name": "Aberdeen North", "lep1_local_enterprise_partnership_name": null, "lep2_local_enterprise_partnership_name": null}\n',  # noqa: E501
    ]
