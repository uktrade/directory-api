import pytest

from django.core import management

from dataservices import models


@pytest.mark.django_db
@pytest.mark.parametrize('model_name, management_cmd, object_count', (
    (models.SuggestedCountry, 'import_suggested_countries', 493),
))
def test_personalisation_import_data_sets(model_name, management_cmd, object_count):
    # importing countries before suggested countries as it has FK to countries
    management.call_command('import_countries')
    management.call_command(management_cmd)
    assert model_name.objects.count() == object_count
