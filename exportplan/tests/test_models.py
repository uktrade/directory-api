import pytest

from exportplan.tests.factories import CompanyExportPlanFactory, CompanyObjectivesFactory


@pytest.mark.django_db
def test_export_plan_answers_count():
    export_plan_vanilla = CompanyExportPlanFactory()

    assert export_plan_vanilla.answers_count == 17

    export_plan_with_related_collection = CompanyExportPlanFactory()
    CompanyObjectivesFactory.create_batch(3, companyexportplan=export_plan_with_related_collection)

    assert export_plan_with_related_collection.answers_count == 18
