import pytest
from exportplan import serializers
from company.tests import factories


@pytest.mark.django_db
def test_company_exportplan_serializer_save():
    company = factories.CompanyFactory.create(number='01234567')
    export_commodity_codes = [{'commodity_name': 'gin', 'commodity_code': '101.2002.123'}]
    export_countries = [{'country_name': 'China', 'country_iso2_code': 'CN'}]
    ui_options = {'target_ages': ['25-34', '35-44']}
    serializer = serializers.CompanyExportPlanSerializer(data={
        'company': company.pk,
        'sso_id': 5,
        "export_commodity_codes": export_commodity_codes,
        "export_countries": export_countries,
        "ui_options": ui_options
    })

    assert serializer.is_valid() is True

    export_plan = serializer.save()

    assert export_plan.company == company
    assert export_plan.export_commodity_codes == export_commodity_codes
    assert export_plan.export_countries == export_countries
    assert export_plan.ui_options == ui_options
    assert export_plan.sso_id == 5


@pytest.mark.django_db
def test_company_exportplan_serializer_export_countries_fail():
    company = factories.CompanyFactory.create(number='01234567')
    serializer = serializers.CompanyExportPlanSerializer(data={
        'company': company.pk,
        'sso_id': 5,
        "export_countries": [{'country_name': None, 'country_iso2_code': 'CN'}],
    })

    assert serializer.is_valid() is False
    assert serializer.errors['export_countries']['country_name']


@pytest.mark.django_db
def test_company_exportplan_serializer_commodity_codes_fail():
    company = factories.CompanyFactory.create(number='01234567')
    serializer = serializers.CompanyExportPlanSerializer(data={
        'company': company.pk,
        'sso_id': 5,
        'export_commodity_codes': [{'commodity_name': None, 'commodity_code': '101.2002.123'}],
    })

    assert serializer.is_valid() is False
    assert serializer.errors['export_commodity_codes']['commodity_name']


@pytest.mark.django_db
def test_export_plan_actions_serializer_fail():
    data = {
        'companyexportplan': None,
        'is_reminders_on': None,
    }
    serializer = serializers.ExportPlanActionsSerializer(data=data)

    assert serializer.is_valid() is False


@pytest.mark.django_db
def test_export_plan_objectives_serializer_fail():
    data = {
        'companyexportplan': None,
        'description': None,
    }
    serializer = serializers.CompanyObjectivesSerializer(data=data)

    assert serializer.is_valid() is False
