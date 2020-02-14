import pytest
from exportplan import serializers
from company.tests import factories


@pytest.mark.django_db
def test_company_exportplan_serializer_save():
    company = factories.CompanyFactory.create(number='01234567')
    export_commodity_codes = ['10101010']
    export_countries = ['CN']
    rules_regs_data = {'rules': '0.001'}
    serializer = serializers.CompanyExportPlanSerializer(data={
        'company': company.pk,
        'sso_id': 5,
        "export_commodity_codes": export_commodity_codes,
        "export_countries": export_countries,
        "rules_regulations": rules_regs_data
    })

    assert serializer.is_valid() is True

    export_plan = serializer.save()

    assert export_plan.company == company
    assert export_plan.export_commodity_codes == export_commodity_codes
    assert export_plan.export_countries == export_countries
    assert export_plan.rules_regulations == rules_regs_data
    assert export_plan.sso_id == 5
