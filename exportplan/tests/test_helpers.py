from unittest.mock import MagicMock, PropertyMock

import pytest

from exportplan import helpers
from exportplan.tests import factories, snapshots


def test_country_code_iso3_to_iso2():
    assert helpers.country_code_iso3_to_iso2('CHN') == 'CN'


def test_country_code_iso3_to_iso2_not_found():
    assert helpers.country_code_iso3_to_iso2('XNY') is None


def test_get_timezone():
    assert helpers.get_timezone('CHN') == 'Asia/Shanghai'


def test_get_local_time_not_found():
    assert helpers.get_timezone('XS') is None


def test_get_iso3_by_country_name():
    assert helpers.get_iso3_by_country_name('Australia') == 'AUS'


def test_get_iso3_by_country_name_upper():
    assert helpers.get_iso3_by_country_name('AUSTRALIA') == 'AUS'


def test_get_iso3_by_country_name_lower():
    assert helpers.get_iso3_by_country_name('australia') == 'AUS'


def test_get_iso3_by_country_name_none():
    assert helpers.get_iso3_by_country_name(None) is None


@pytest.mark.django_db
@pytest.mark.parametrize(
    'existing_indices, expected',
    [
        [[], 0],
        [[0], 1],
        [[0, 1], 2],
        [[0, 2], 1],
        [[1, 2], 0],
    ],
)
def test_get_unique_exportplan_name(existing_indices, expected, authed_supplier):
    def get_name(id):
        postscript = f' ({id})' if id else ''
        return f'Export plan for selling cheese to Russia{postscript}'

    for idx in existing_indices:
        factories.CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id, name=get_name(idx))
    ep = {
        'sso_id': authed_supplier.sso_id,
        'export_commodity_codes': [{'commodity_name': 'cheese'}],
        'export_countries': [{'country_name': 'Russia'}],
    }
    new_name = helpers.get_unique_exportplan_name(ep)
    assert new_name == get_name(expected)


@pytest.mark.django_db
def test_get_unique_exportplan_name_empty():
    product = {'commodity_name': 'cheese'}
    country = {'country_name': 'Russia'}
    ep_both = {
        'sso_id': 100,
        'export_commodity_codes': [product],
        'export_countries': [country],
    }
    ep_no_product = {
        'sso_id': 101,
        'export_commodity_codes': [],
        'export_countries': [country],
    }
    ep_no_country = {
        'sso_id': 102,
        'export_commodity_codes': [product],
        'export_countries': [],
    }
    ep_nothing = {
        'sso_id': 103,
        'export_commodity_codes': [],
        'export_countries': [],
    }
    assert helpers.get_unique_exportplan_name(ep_both) == 'Export plan for selling cheese to Russia'
    assert helpers.get_unique_exportplan_name(ep_no_product) == 'Export plan'
    assert helpers.get_unique_exportplan_name(ep_no_country) == 'Export plan'
    assert helpers.get_unique_exportplan_name(ep_nothing) == 'Export plan'


def test_dictfetchall():
    rows = [('mock_row_content_1', 1), ('mock_row_content_2', 2), ('mock_row_content_3', 3)]
    cursor_description = (('some_str', 0), ('some_num', 1005))

    mock_cursor = MagicMock()
    mock_description = PropertyMock(return_value=cursor_description)
    mock_cursor.fetchall.return_value = rows
    type(mock_cursor).description = mock_description

    expected = [
        {'some_num': 1, 'some_str': 'mock_row_content_1'},
        {'some_num': 2, 'some_str': 'mock_row_content_2'},
        {'some_num': 3, 'some_str': 'mock_row_content_3'},
    ]

    assert helpers.dictfetchall(mock_cursor) == expected


def test_build_query():
    test_id = '123'
    test_ts = '2022-07-01T15:19:11.031368'
    query = helpers.build_query(test_id, test_ts)
    assert query.strip() == snapshots.BUILD_QUERY_SNAPSHOT.strip()
