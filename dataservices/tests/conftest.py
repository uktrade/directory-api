import pytest
from dataservices import models


@pytest.fixture
def internet_usage_data():
    country_data = [
        models.InternetUsage(
            country_code='GBR',
            country_name='United Kingdom',
            year=2020,
            value=90.97,
        ),
        models.InternetUsage(
            country_code='DEU',
            country_name='Germany',
            year=2020,
            value=91.97
        )
    ]
    yield models.InternetUsage.objects.bulk_create(country_data)
    models.InternetUsage.objects.all().delete()
