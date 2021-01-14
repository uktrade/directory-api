from unittest import mock

import pytest
from django.core import management
from import_export import results

from dataservices import models


@pytest.mark.django_db
@pytest.mark.parametrize(
    'model_name, management_cmd, object_count',
    (
        (models.CorruptionPerceptionsIndex, 'import_cpi_data', 180),
        (models.EaseOfDoingBusiness, 'import_easeofdoingbusiness_data', 264),
        (models.WorldEconomicOutlook, 'import_weo_data', 1552),
        (models.InternetUsage, 'import_internet_usage_data', 264),
        (models.ConsumerPriceIndex, 'import_consumer_price_index_data', 264),
    ),
)
def test_import_data_sets(model_name, management_cmd, object_count):
    model_name.objects.create(country_name='abc', country_code='a')
    management.call_command(management_cmd)
    assert model_name.objects.count() == object_count


@pytest.mark.django_db
@mock.patch.object(results.Result, 'has_errors', mock.Mock(return_value=True))
@pytest.mark.parametrize(
    'management_cmd',
    [
        'import_cpi_data',
        'import_easeofdoingbusiness_data',
        'import_weo_data',
        'import_internet_usage_data',
        'import_consumer_price_index_data',
    ],
)
def test_import_data_sets_error(management_cmd):
    management.call_command(management_cmd)
    assert models.CorruptionPerceptionsIndex.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    'model_name, management_cmd, object_count',
    (
        (models.Country, 'import_countries', 194),
        (models.GDPPerCapita, 'import_gdp_per_capita_data', 264),
        (models.RuleOfLaw, 'import_rank_of_law_data', 131),
    ),
)
def test_import_countries_data_sets(model_name, management_cmd, object_count):
    management.call_command(management_cmd)
    assert model_name.objects.count() == object_count


@pytest.mark.django_db
def test_import_rank_of_law_data_with_no_country():
    management.call_command('import_rank_of_law_data')
    rule_of_law = models.RuleOfLaw.objects.first()

    assert rule_of_law.country is None
