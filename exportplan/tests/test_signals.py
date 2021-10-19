import pytest

from . import factories


@pytest.mark.parametrize(
    'export_commodity_codes, export_countries, label_name',
    [
        [[], [], None],
        [[{'commodity_name': 'gin', 'commodity_code': '101.2002.123'}], [], None],
        [[], [{'country_name': 'China', 'country_iso2_code': 'CN'}], None],
        [
            [{'commodity_name': 'gin', 'commodity_code': '101.2002.123'}],
            [{'country_name': 'China', 'country_iso2_code': 'CN'}],
            'Export plan for selling gin to China',
        ],
    ],
)
@pytest.mark.django_db
def test_update_label(export_commodity_codes, export_countries, label_name):
    ep = factories.CompanyExportPlanFactory(export_commodity_codes=[], export_countries=[])
    ep.refresh_from_db()
    assert ep.name is None
    ep.export_commodity_codes = export_commodity_codes
    ep.export_countries = export_countries
    ep.save()
    ep.refresh_from_db()
    assert ep.name == label_name


@pytest.mark.django_db
def test_update_label_with_previous_state():
    ep = factories.CompanyExportPlanFactory(export_commodity_codes=[], export_countries=[], name='Test')
    ep.refresh_from_db()
    assert ep.name == 'Test'
    ep.export_commodity_codes = [{'commodity_name': 'gin', 'commodity_code': '101.2002.123'}]
    ep.save()
    ep.refresh_from_db()
    assert ep.name == 'Test'

    ep.export_countries = [{'country_name': 'China', 'country_iso2_code': 'CN'}]
    ep.save()
    ep.refresh_from_db()
    assert ep.name == 'Export plan for selling gin to China'

    ep.export_countries = [{'country_name': 'Spain', 'country_iso2_code': 'SP'}]
    ep.save()
    ep.refresh_from_db()
    assert ep.name == 'Export plan for selling gin to China'
