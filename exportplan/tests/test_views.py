import pytest

from datetime import date
from django.urls import reverse
import http
from conf import settings

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
            'owner': None, 'start_date': None, 'end_date': None,  'planned_reviews': '', 'pk': 1,
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
        'brand_product_details': export_plan.brand_product_details,
        'rational': export_plan.rational,
        'sectors': export_plan.sectors,
        'consumer_demand': export_plan.consumer_demand,
        'target_markets': export_plan.target_markets,
        'compliance': export_plan.compliance,
        'export_certificates': export_plan.export_certificates,
        'route_to_markets': export_plan.route_to_markets,
        'promotion_channels': export_plan.promotion_channels,
        'resource_needed': export_plan.resource_needed,
        'spend_marketing': export_plan.spend_marketing,
        'research_consumer_demand': export_plan.research_consumer_demand,
        'research_competition': export_plan.research_competition,
        'research_product_trends': export_plan.research_product_trends,
        'research_unique_selling': export_plan.research_unique_selling,
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
                'planned_reviews': 'None planned',
                'owner': None,
                'start_date': None,
                'end_date': None,
                'pk': export_plan.company_objectives.all()[0].pk,

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
def test_export_plan_target_markets_update_historical_disabled(authed_client, authed_supplier):
    settings.FEATURE_COMTRADE_HISTORICAL_DATA_ENABLED = False
    CompanyExportPlan.objects.all().delete()
    export_plan = CompanyExportPlanFactory.create()
    CompanyObjectivesFactory.create(companyexportplan=export_plan)
    ExportPlanActionsFactory.create(companyexportplan=export_plan)

    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})

    data = {'target_markets': export_plan.target_markets + [{'country': 'Australia', 'export_duty': 1.5}]}

    response = authed_client.patch(url, data, format='json')
    export_plan.refresh_from_db()

    assert response.status_code == http.client.OK
    country_market_data = {
        'country': 'Mexico', 'export_duty': '1.5',
        'last_year_data': {'import_value': {'year': 2019, 'trade_value': 100}},
        'easeofdoingbusiness': {'total': 1, 'year_2019': 20, 'country_code': 'AUS', 'country_name': 'Australia'},
        'corruption_perceptions_index':
            {
                'rank': 21, 'country_code': 'AUS', 'country_name': 'Australia', 'cpi_score_2019': 24
             },
        'timezone': 'America/Mexico_City',
        'utz_offset': '-0500',
        'world_economic_outlook_data': [{'year_2019': 20, 'country_code': 'AUS', 'country_name': 'Australia'}],
        'cia_factbook_data': {'capital': 'London', 'currency': 'GBP', 'population': '60m'},
        'commodity_name': 'Gin',
    }
    assert export_plan.target_markets[0] == country_market_data
    country_market_data['country'] = 'Australia'
    country_market_data['utz_offset'] = '+1030'
    country_market_data['timezone'] = 'Australia/Lord_Howe'
    assert export_plan.target_markets[1] == country_market_data


@pytest.mark.django_db
def test_export_plan_target_markets_update_historical_enabled(authed_client, authed_supplier):
    settings.FEATURE_COMTRADE_HISTORICAL_DATA_ENABLED = True
    export_plan = CompanyExportPlanFactory.create()
    CompanyObjectivesFactory.create(companyexportplan=export_plan)
    ExportPlanActionsFactory.create(companyexportplan=export_plan)

    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})

    data = {'target_markets': export_plan.target_markets + [{'country': 'Australia', 'export_duty': 1.5}]}

    response = authed_client.patch(url, data, format='json')
    export_plan.refresh_from_db()

    assert response.status_code == http.client.OK

    country_market_data = {
        'country': 'Mexico', 'export_duty': '1.5',
        'last_year_data': {'import_value': {'year': 2019, 'trade_value': 100}},
        'easeofdoingbusiness': {'total': 1, 'year_2019': 20, 'country_code': 'AUS', 'country_name': 'Australia'},
        'corruption_perceptions_index':
            {
                'rank': 21, 'country_code': 'AUS', 'country_name': 'Australia', 'cpi_score_2019': 24
             },
        'historical_import_data': {'historical_trade_value_all': {'2016': 350, '2017': 350, '2018': 350},
                                   'historical_trade_value_partner': {'2016': 50, '2017': 100, '2018': 200}},
        'timezone': 'America/Mexico_City',
        'utz_offset': '-0500',
        'world_economic_outlook_data': [{'year_2019': 20, 'country_code': 'AUS', 'country_name': 'Australia'}],
        'cia_factbook_data': {'capital': 'London', 'currency': 'GBP', 'population': '60m'},
        'commodity_name': 'Gin',
    }

    assert export_plan.target_markets[0] == country_market_data
    country_market_data['country'] = 'Australia'
    country_market_data['utz_offset'] = '+1030'
    country_market_data['timezone'] = 'Australia/Lord_Howe'
    assert export_plan.target_markets[1] == country_market_data
    settings.FEATURE_COMTRADE_HISTORICAL_DATA_ENABLED = False


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


@pytest.mark.django_db
def test_export_plan_objectives_update(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    my_objective = export_plan.company_objectives.all()[0]
    url = reverse('export-plan-objectives-detail-update', kwargs={'pk': my_objective.pk})

    data = {'description': 'updated now'}

    response = authed_client.patch(url, data, format='json')
    my_objective.refresh_from_db()

    assert response.status_code == http.client.OK
    assert my_objective.description == 'updated now'


@pytest.mark.django_db
def test_export_plan_objectives_retrieve(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    my_objective = export_plan.company_objectives.all()[0]
    url = reverse('export-plan-objectives-detail-update', kwargs={'pk': my_objective.pk})

    response = authed_client.get(url)
    data = response.json()
    assert response.status_code == http.client.OK
    assert my_objective.description == data['description']
    assert my_objective.pk == data['pk']
    assert my_objective.start_date == data['start_date']
    assert my_objective.start_date == data['end_date']


@pytest.mark.django_db
def test_export_plan_objectives_create(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-objectives-list-create')

    data = {
            'companyexportplan': export_plan.id,
            'description': 'newly created',
            'planned_reviews': 'None planned',
        }

    response = authed_client.post(url, data)

    data = response.json()

    assert response.status_code == http.client.CREATED
    export_plan.refresh_from_db()
    assert export_plan.company_objectives.all().count() == 2
    my_objective = export_plan.company_objectives.all()[0]

    assert my_objective.description == data['description']
    assert my_objective.pk == data['pk']
    assert my_objective.planned_reviews == data['planned_reviews']


@pytest.mark.django_db
def test_export_plan_objectives_delete(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    my_objective = export_plan.company_objectives.all()[0]
    url = reverse('export-plan-objectives-detail-update', kwargs={'pk': my_objective.pk})

    response = authed_client.delete(url)
    assert response.status_code == http.client.NO_CONTENT
    assert not export_plan.company_objectives.all()
