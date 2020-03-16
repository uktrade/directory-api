import pytest
from django.urls import reverse
import http

from exportplan import models
from exportplan.tests.factories import CompanyExportPlanFactory
from company.tests.factories import CompanyFactory


@pytest.fixture
def company():
    return CompanyFactory.create(number='01234567')


@pytest.fixture
def export_plan_data(company):
    return {
        'company': company.pk,
        'export_commodity_codes': ['10101010', ],
        'export_countries': ['CN', ],
        'rules_regulations': {'rules': '0.001'},
        'company_objectives': [{'description': 'export 5k cases of wine'}, ]
    }


@pytest.mark.django_db
def test_export_plan_create(export_plan_data, authed_client, authed_supplier):
    response = authed_client.post(
        reverse('export-plan-list-create'), export_plan_data, format='json'
    )
    assert response.status_code == http.client.CREATED

    instance = models.CompanyExportPlan.objects.get(pk=response.data['pk'])

    assert instance.export_commodity_codes == export_plan_data['export_commodity_codes']
    assert instance.export_countries == export_plan_data['export_countries']
    assert instance.rules_regulations == export_plan_data['rules_regulations']

    # Relationship manager returned I want serialized list instead
    assert instance.company_objectives.all() == [{'description': 'export 5k cases of wine'}, ]
    assert instance.sso_id == authed_supplier.sso_id


@pytest.mark.django_db
def test_export_plan_list(authed_client, authed_supplier):
    CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)
    CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)
    CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id+1)

    response = authed_client.get(reverse('export-plan-list-create'))

    assert len(response.json()) == 2
    assert response.status_code == 200


@pytest.mark.django_db
def test_export_plan_retrieve(authed_client, authed_supplier, company,):
    export_plan = CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)
    authed_supplier.company = company
    authed_supplier.save()
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})
    response = authed_client.get(url)
    data = {
        'company': export_plan.company.id,
        'sso_id': authed_supplier.sso_id,
        'export_commodity_codes': export_plan.export_commodity_codes,
        'export_countries': export_plan.export_countries,
        'rules_regulations': export_plan.rules_regulations,
        'rational': export_plan.rational,
        'planned_review': export_plan.planned_review,
        'sectors': export_plan.sectors,
        'consumer_demand': export_plan.consumer_demand,
        'target_countries': export_plan.target_countries,
        'compliance': export_plan.compliance,
        'export_certificates': export_plan.export_certificates,
        'route_to_markets': export_plan.route_to_markets,
        'promotion_channels': export_plan.promotion_channels,
        'resource_needed': export_plan.resource_needed,
        'spend_marketing': export_plan.spend_marketing,
        'pk': export_plan.pk
    }
    assert response.status_code == 200
    assert response.json() == data


@pytest.mark.django_db
def test_export_plan_update(authed_client, authed_supplier, company,):
    export_plan = CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)
    authed_supplier.company = company
    authed_supplier.save()
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})

    data = {'export_commodity_codes': ['2015.01.20.15']}
    assert export_plan.export_commodity_codes != data['export_commodity_codes']

    response = authed_client.patch(url, data, format='json')
    export_plan.refresh_from_db()

    assert response.status_code == http.client.OK
    assert export_plan.export_commodity_codes == data['export_commodity_codes']
