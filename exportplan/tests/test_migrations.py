import pytest


@pytest.mark.django_db
def test_create_multiple_products_markets(migration):

    old_apps = migration.before([('exportplan', '0039_auto_20210721_1434')])
    Exportplan = old_apps.get_model('exportplan', 'CompanyExportPlan')

    Exportplan.objects.create(sso_id=0, export_countries=[{'country_name': 'China', 'country_iso2_code': 'CN'}])
    Exportplan.objects.create(sso_id=0, export_countries=[{'country_name': 'India', 'country_iso2_code': 'IN'}])

    migration.apply('exportplan', '0040_migrate_multi_products_markets')
