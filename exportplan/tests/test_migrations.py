from exportplan.tests.factories import CompanyExportPlanFactory


# Export plan tests the migration of test_populate_exportplan_name once this has been run in production then we can
# remove this test and set --nomigration in pytest.ini to speed up the running of tests
def test_populate_exportplan_name(migration):

    ep_no_countries = CompanyExportPlanFactory(export_countries=[])
    ep_no_product = CompanyExportPlanFactory(export_commodity_codes=[])
    ep_no_product_no_counties = CompanyExportPlanFactory(export_commodity_codes=[], export_countries=[])
    ep_populated = CompanyExportPlanFactory()
    ep_populated_with_name = CompanyExportPlanFactory(name='do not override')

    migration.before([('exportplan', '0041_derive_export_end_date')])
    migration.apply('exportplan', '0042_populate_exportplan_name')

    ep_no_countries.refresh_from_db()
    ep_no_product.refresh_from_db()
    ep_no_product_no_counties.refresh_from_db()
    ep_populated.refresh_from_db()
    ep_populated_with_name.refresh_from_db()

    assert ep_no_countries.name == 'Export plan'
    assert ep_no_product.name == 'Export plan'
    assert ep_no_product_no_counties.name == 'Export plan'
    assert ep_populated.name == 'Export plan for selling gin to China'
    assert ep_populated_with_name.name == 'do not override'
