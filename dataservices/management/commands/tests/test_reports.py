import pytest
from django.core import management


@pytest.mark.django_db
def test_report_country_population_data_sets():
    management.call_command('report_population_data_lookups')
