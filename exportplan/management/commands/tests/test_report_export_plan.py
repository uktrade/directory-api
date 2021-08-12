import pytest
from django.core import management

def test_report_export_plan():
    print("test_export_plan_HAHAHA")
    management.call_command('report_export_plan')
    assert False