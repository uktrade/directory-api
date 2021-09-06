from exportplan.management.commands import report_helper
from exportplan.management.commands.tests.test_report_export_plan import export_plan_country_no_data

import pytest


@pytest.mark.django_db
def test_is_ep_plan_empty_with_no_ui_progress(export_plan_country_no_data):
    plan = export_plan_country_no_data
    ep_empty = report_helper.is_ep_plan_empty(plan, report_helper.set_useable_fields())
    assert ep_empty == True
