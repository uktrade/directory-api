import pytest
from unittest import mock
from django.urls import reverse
import http

from exportplan import models
from exportplan.tests.factories import CompanyExportPlanFactory
from company.tests.factories import CompanyFactory


@pytest.fixture
def company():
    return CompanyFactory.create(number='01234567')


@pytest.fixture
def exportplan_data(company):
    return {
        'company': company.pk,
        'export_commodity_codes': ['10101010', ],
        'export_countries': ['CN', ],
    }


@pytest.mark.django_db
def test_export_plan_create(exportplan_data, authed_client, authed_supplier, company,):

    response = authed_client.post(
        reverse('export-plan-list-create'), exportplan_data, format='json'
    )
    assert response.status_code == http.client.CREATED

    instance = models.CompanyExportPlan.objects.get(pk=response.data['pk'])
    assert instance.export_commodity_codes == exportplan_data['export_commodity_codes']
    assert instance.export_countries == exportplan_data['export_countries']
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
    exportplan= CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)

    authed_supplier.company = company
    authed_supplier.save()
    url = reverse('export-plan-retrieve-detail-update', kwargs={'pk': exportplan.pk})
    response = authed_client.get(url)
    data = {
        'company': exportplan.company.id,
        'sso_id': authed_supplier.sso_id,
        'export_commodity_codes': exportplan.export_commodity_codes,
        'export_countries': exportplan.export_countries,
        'pk': exportplan.pk
    }
    assert response.status_code == 200
    assert response.json() == data


@pytest.mark.django_db
def test_export_plan_update(authed_client, authed_supplier, company,):
    exportplan= CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)

    authed_supplier.company = company
    authed_supplier.save()
    url = reverse('export-plan-retrieve-detail-update', kwargs={'pk': exportplan.pk})

    data = {'export_commodity_codes': ['2015.01.20.15']}
    assert exportplan.export_commodity_codes != data['export_commodity_codes']

    response = authed_client.patch(url, data, format='json')
    exportplan.refresh_from_db()

    assert response.status_code == http.client.OK
    assert exportplan.export_commodity_codes == data['export_commodity_codes']
