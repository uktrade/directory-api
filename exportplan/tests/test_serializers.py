import pytest

from company.tests import factories
from exportplan import serializers


@pytest.mark.django_db
def test_company_exportplan_serializer_save():
    company = factories.CompanyFactory.create(number='01234567')
    ui_options = {'target_ages': ['25-34', '35-44']}

    serializer = serializers.CompanyExportPlanSerializer(
        data={
            'company': company.pk,
            'sso_id': 5,
            "ui_options": ui_options,
        }
    )
    assert serializer.is_valid() is True

    export_plan = serializer.save()

    assert export_plan.company == company
    assert export_plan.ui_options == ui_options
    assert export_plan.sso_id == 5


@pytest.mark.django_db
def test_export_plan_objectives_serializer_fail():
    data = {
        'companyexportplan': None,
        'description': None,
    }
    serializer = serializers.CompanyObjectivesSerializer(data=data)

    assert serializer.is_valid() is False
