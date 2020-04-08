import pytest

from datetime import date
from django.urls import reverse
import http

from exportplan.tests.factories import CompanyExportPlanFactory, CompanyObjectivesFactory, ExportPlanActionsFactory
from company.tests.factories import CompanyFactory
from exportplan.models import CompanyExportPlan


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
        'company_objectives': [{'description': 'export 5k cases of wine'}, ],
        'export_plan_actions': [{'is_reminders_on': True, 'action_type': 'TARGET_MARKETS', }]
    }


@pytest.fixture
def export_plan():
    export_plan = CompanyExportPlanFactory.create()
    CompanyObjectivesFactory.create(companyexportplan=export_plan)
    ExportPlanActionsFactory.create(companyexportplan=export_plan)
    return export_plan


@pytest.mark.django_db
def test_export_plan_create(export_plan_data, authed_client, authed_supplier):
    response = authed_client.post(
        reverse('export-plan-list-create'), export_plan_data, format='json'
    )
    assert response.status_code == http.client.CREATED
    created_export_plan = response.json()

    export_plan_db = CompanyExportPlan.objects.last()

    assert created_export_plan['export_commodity_codes'] == export_plan_data['export_commodity_codes']
    assert created_export_plan['export_countries'] == export_plan_data['export_countries']
    assert created_export_plan['rules_regulations'] == export_plan_data['rules_regulations']
    assert created_export_plan['export_plan_actions'] == [
        {
            'companyexportplan': export_plan_db.pk, 'owner': None, 'due_date': None,
            'is_reminders_on': True, 'action_type': 'TARGET_MARKETS',
        }
    ]

    assert created_export_plan['company_objectives'] == [
        {
            'companyexportplan': export_plan_db.pk, 'description': 'export 5k cases of wine',
            'owner': None, 'start_date': None, 'end_date': None,
        }
    ]
    assert created_export_plan['sso_id'] == authed_supplier.sso_id


@pytest.mark.django_db
def test_export_plan_list(authed_client, authed_supplier):
    CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)
    CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)
    CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id+1)

    response = authed_client.get(reverse('export-plan-list-create'))

    assert len(response.json()) == 2
    assert response.status_code == 200


@pytest.mark.django_db
def test_export_plan_retrieve(authed_client, authed_supplier, export_plan):

    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})
    response = authed_client.get(url)

    data = {
        'company': export_plan.company.id,
        'sso_id': export_plan.sso_id,
        'export_commodity_codes': export_plan.export_commodity_codes,
        'export_countries': export_plan.export_countries,
        'rules_regulations': export_plan.rules_regulations,
        'rational': export_plan.rational,
        'planned_review': export_plan.planned_review,
        'sectors': export_plan.sectors,
        'consumer_demand': export_plan.consumer_demand,
        'target_markets': export_plan.target_markets,
        'compliance': export_plan.compliance,
        'export_certificates': export_plan.export_certificates,
        'route_to_markets': export_plan.route_to_markets,
        'promotion_channels': export_plan.promotion_channels,
        'resource_needed': export_plan.resource_needed,
        'spend_marketing': export_plan.spend_marketing,
        'export_plan_actions': [
            {
                'companyexportplan': export_plan.id,
                'owner': None, 'due_date': None,
                'is_reminders_on': False,
                'action_type': 'TARGET_MARKETS',
            }
        ],
        'company_objectives': [
            {
                'companyexportplan': export_plan.id,
                'description': 'export 5k cases of wine',
                'owner': None,
                'start_date': None,
                'end_date': None,
            }
        ],
        'pk': export_plan.pk
    }
    assert response.status_code == 200
    assert response.json() == data


@pytest.mark.django_db
def test_export_plan_update(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})

    data = {'export_commodity_codes': ['2015.01.20.15']}
    assert export_plan.export_commodity_codes != data['export_commodity_codes']

    response = authed_client.patch(url, data, format='json')
    export_plan.refresh_from_db()

    assert response.status_code == http.client.OK
    assert export_plan.export_commodity_codes == data['export_commodity_codes']


@pytest.mark.django_db
def test_export_plan_target_markets_update(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})

    data = {'target_markets': export_plan.target_markets + [{'country': 'Australia', 'export_duty': 1.5}]}

    response = authed_client.patch(url, data, format='json')
    export_plan.refresh_from_db()

    assert response.status_code == http.client.OK
    country_market_data = {
        'country': 'UK', 'export_duty': '1.5', 'last_year_data': {'import_value': {'year': 2019, 'trade_value': 100}},
        'easeofdoingbusiness': {'total': 1, 'year_2019': 20, 'country_code': 'AUS', 'country_name': 'Australia'},
        'corruption_perceptions_index':
            {
                'rank': 21, 'country_code': 'AUS', 'country_name': 'Australia', 'cpi_score_2019': 24
             },
        'historical_import_data': {'historical_trade_value_all': {'2016': 350, '2017': 350, '2018': 350},
                                   'historical_trade_value_partner': {'2016': 50, '2017': 100, '2018': 200}},
        'timezone': 'Australia/Lord_Howe',
        'utz_offset': '+1030',
        'commodity_name': 'Gin',
    }

    assert export_plan.target_markets[0] == country_market_data
    country_market_data['country'] = 'Australia'
    assert export_plan.target_markets[1] == country_market_data


@pytest.mark.django_db
def test_export_plan_update_objectives(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    company_objective_db = export_plan.company_objectives.all()[0]
    company_objective = {
        'companyexportplan': export_plan.id,
        'description': 'This is an update',
        'owner': company_objective_db.owner,
        'start_date': company_objective_db.start_date,
        'end_date': company_objective_db.end_date,
    }
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})

    data = {'company_objectives': [company_objective]}
    response = authed_client.patch(url, data, format='json')
    export_plan.refresh_from_db()
    assert response.status_code == http.client.OK

    assert len(export_plan.company_objectives.all()) == 1
    company_objectives_updated = export_plan.company_objectives.all()[0]
    assert company_objectives_updated.description == company_objective['description']
    assert company_objectives_updated.owner == company_objective['owner']
    assert company_objectives_updated.companyexportplan.id == company_objective['companyexportplan']
    assert company_objectives_updated.start_date == company_objective['start_date']
    assert company_objectives_updated.description == company_objective['description']
    assert company_objectives_updated.end_date == company_objective['end_date']


@pytest.mark.django_db
def test_export_plan_new_actions(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    actions = [
        {'is_reminders_on': True, 'due_date': '2020-01-01'},
        {'is_reminders_on': False, 'due_date': '2020-01-02'}
    ]
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})
    data = {'export_plan_actions': actions}

    response = authed_client.patch(url, data, format='json')

    export_plan.refresh_from_db()
    assert response.status_code == http.client.OK
    export_plan_actions = export_plan.export_plan_actions.all()
    assert len(export_plan_actions) == 2
    assert export_plan_actions[0].is_reminders_on is False
    assert export_plan_actions[0].due_date == date(2020, 1, 2)
    assert export_plan_actions[1].is_reminders_on is True
    assert export_plan_actions[1].due_date == date(2020, 1, 1)
