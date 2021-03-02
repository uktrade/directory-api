import http
from datetime import date

import pytest
from directory_constants import choices
from django.urls import reverse

from company.tests.factories import CompanyFactory
from conf import settings
from exportplan import models
from exportplan.tests import factories


@pytest.fixture
def company():
    return CompanyFactory.create(number='01234567')


@pytest.fixture
def export_plan_data(company):
    return {
        'company': company.pk,
        'export_commodity_codes': [{'commodity_name': 'gin', 'commodity_code': '101.2002.123'}],
        'export_countries': [{'country_name': 'China', 'country_iso2_code': 'CN'}],
        'ui_options': {'target_ages': ['25-34', '35-44']},
        'ui_progress': {'target-markets': {'is_complete': False}},
        'adaptation_target_market': {'labelling': 'manual', 'size': '2l'},
        'overhead_costs': {'product_adaption': '13.02', 'other_overhead_costs': '19.23'},
        'direct_costs': {'product_costs': '12.02', 'labour_costs': '13.02'},
        'total_cost_and_price': {'average_price_per_unit': '23.44'},
        'company_objectives': [
            {'description': 'export 5k cases of wine'},
        ],
        'export_plan_actions': [
            {
                'is_reminders_on': True,
                'action_type': 'TARGET_MARKETS',
            }
        ],
    }


@pytest.fixture
def export_plan():
    export_plan = factories.CompanyExportPlanFactory.create()
    factories.CompanyObjectivesFactory.create(companyexportplan=export_plan)
    factories.ExportPlanActionsFactory.create(companyexportplan=export_plan)
    factories.RouteToMarketsFactory.create(companyexportplan=export_plan)
    factories.TargetMarketDocumentsFactory.create(companyexportplan=export_plan)
    factories.FundingCreditOptionsFactory.create(companyexportplan=export_plan)
    factories.BusinessTripsFactory.create(companyexportplan=export_plan)
    factories.BusinessRiskFactory.create(companyexportplan=export_plan)
    return export_plan


@pytest.mark.django_db
def test_export_plan_create(export_plan_data, authed_client, authed_supplier):
    response = authed_client.post(reverse('export-plan-list-create'), export_plan_data, format='json')
    assert response.status_code == http.client.CREATED
    created_export_plan = response.json()

    export_plan_db = models.CompanyExportPlan.objects.last()

    assert created_export_plan['export_commodity_codes'] == export_plan_data['export_commodity_codes']
    assert created_export_plan['export_countries'] == export_plan_data['export_countries']
    assert created_export_plan['ui_options'] == export_plan_data['ui_options']
    assert created_export_plan['ui_progress'] == export_plan_data['ui_progress']
    assert created_export_plan['total_cost_and_price'] == export_plan_data['total_cost_and_price']
    assert created_export_plan['overhead_costs'] == export_plan_data['overhead_costs']
    assert created_export_plan['direct_costs'] == export_plan_data['direct_costs']
    assert created_export_plan['export_plan_actions'] == [
        {
            'companyexportplan': export_plan_db.pk,
            'owner': None,
            'due_date': None,
            'is_reminders_on': True,
            'action_type': 'TARGET_MARKETS',
        }
    ]

    assert created_export_plan['company_objectives'] == [
        {
            'companyexportplan': export_plan_db.pk,
            'description': 'export 5k cases of wine',
            'owner': None,
            'start_date': None,
            'end_date': None,
            'planned_reviews': '',
            'pk': 1,
        }
    ]
    assert created_export_plan['sso_id'] == authed_supplier.sso_id


@pytest.mark.django_db
def test_export_plan_list(authed_client, authed_supplier):
    factories.CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)
    factories.CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)
    factories.CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id + 1)

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
        'ui_options': export_plan.ui_options,
        'ui_progress': export_plan.ui_progress,
        'about_your_business': export_plan.about_your_business,
        'objectives': export_plan.objectives,
        'sectors': export_plan.sectors,
        'consumer_demand': export_plan.consumer_demand,
        'target_markets': export_plan.target_markets,
        'compliance': export_plan.compliance,
        'export_certificates': export_plan.export_certificates,
        'marketing_approach': export_plan.marketing_approach,
        'promotion_channels': export_plan.promotion_channels,
        'resource_needed': export_plan.resource_needed,
        'spend_marketing': export_plan.spend_marketing,
        'target_markets_research': export_plan.target_markets_research,
        'adaptation_target_market': export_plan.adaptation_target_market,
        'direct_costs': export_plan.direct_costs,
        'overhead_costs': export_plan.overhead_costs,
        'total_cost_and_price': export_plan.total_cost_and_price,
        'export_plan_actions': [
            {
                'companyexportplan': export_plan.id,
                'owner': None,
                'due_date': None,
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
        'route_to_markets': [
            {
                'companyexportplan': export_plan.id,
                'route': export_plan.route_to_markets.all()[0].route,
                'promote': export_plan.route_to_markets.all()[0].promote,
                'market_promotional_channel': export_plan.route_to_markets.all()[0].market_promotional_channel,
                'pk': export_plan.route_to_markets.all()[0].pk,
            }
        ],
        'target_market_documents': [
            {
                'companyexportplan': export_plan.id,
                'document_name': export_plan.target_market_documents.all()[0].document_name,
                'note': export_plan.target_market_documents.all()[0].note,
                'pk': export_plan.target_market_documents.all()[0].pk,
            }
        ],
        'funding_credit_options': [
            {
                'companyexportplan': export_plan.id,
                'funding_option': export_plan.funding_credit_options.all()[0].funding_option,
                'amount': float(export_plan.funding_credit_options.all()[0].amount),
                'pk': export_plan.funding_credit_options.all()[0].pk,
            }
        ],
        'funding_and_credit': export_plan.funding_and_credit,
        'getting_paid': export_plan.getting_paid,
        'travel_business_policies': export_plan.travel_business_policies,
        'business_trips': [
            {
                'companyexportplan': export_plan.id,
                'pk': export_plan.business_trips.all()[0].pk,
                'note': export_plan.business_trips.all()[0].note,
            }
        ],
        'business_risks': [
            {
                'companyexportplan': export_plan.id,
                'pk': export_plan.business_risks.all()[0].pk,
                'risk': export_plan.business_risks.all()[0].risk,
                'contingency_plan': export_plan.business_risks.all()[0].contingency_plan,
                'risk_likelihood': export_plan.business_risks.all()[0].risk_likelihood,
                'risk_impact': export_plan.business_risks.all()[0].risk_impact,
            }
        ],
        'pk': export_plan.pk,
    }
    assert response.status_code == 200
    assert response.json() == data


@pytest.mark.django_db
def test_export_plan_update(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})

    data = {'export_commodity_codes': [{'commodity_name': 'vodka', 'commodity_code': '104.2402.123'}]}
    assert export_plan.export_commodity_codes != data['export_commodity_codes']

    response = authed_client.patch(url, data, format='json')
    export_plan.refresh_from_db()

    assert response.status_code == http.client.OK
    assert export_plan.export_commodity_codes == data['export_commodity_codes']


@pytest.mark.django_db
def test_export_plan_target_markets_update_historical_disabled(authed_client, authed_supplier):
    settings.FEATURE_COMTRADE_HISTORICAL_DATA_ENABLED = False
    models.CompanyExportPlan.objects.all().delete()
    export_plan = factories.CompanyExportPlanFactory.create()
    factories.CompanyObjectivesFactory.create(companyexportplan=export_plan)
    factories.ExportPlanActionsFactory.create(companyexportplan=export_plan)

    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})

    data = {
        'target_markets': export_plan.target_markets
        + [
            {
                'country': 'Australia',
            }
        ]
    }

    response = authed_client.patch(url, data, format='json')
    export_plan.refresh_from_db()

    assert response.status_code == http.client.OK
    country_market_data = {
        'country': 'Mexico',
        'last_year_data': {'import_value': {'year': 2019, 'trade_value': 100}},
        'easeofdoingbusiness': {'total': 1, 'year_2019': 20, 'country_code': 'AUS', 'country_name': 'Australia'},
        'corruption_perceptions_index': {
            'rank': 21,
            'country_code': 'AUS',
            'country_name': 'Australia',
            'cpi_score': 24,
        },
        'timezone': 'America/Mexico_City',
        'utz_offset': '-0500',
        'world_economic_outlook_data': [{'year_2019': 20, 'country_code': 'AUS', 'country_name': 'Australia'}],
        'cia_factbook_data': {'capital': 'London', 'currency': 'GBP', 'population': '60m'},
    }
    # We can't compare actual time offsets as these vary over time
    country_market_data['utz_offset'] = export_plan.target_markets[0]['utz_offset']
    assert export_plan.target_markets[0] == country_market_data
    country_market_data['country'] = 'Australia'
    country_market_data['utz_offset'] = export_plan.target_markets[1]['utz_offset']
    country_market_data['timezone'] = 'Australia/Lord_Howe'
    assert export_plan.target_markets[1] == country_market_data


@pytest.mark.django_db
def test_export_plan_target_markets_update_historical_enabled(authed_client, authed_supplier):
    settings.FEATURE_COMTRADE_HISTORICAL_DATA_ENABLED = True
    export_plan = factories.CompanyExportPlanFactory.create()
    factories.CompanyObjectivesFactory.create(companyexportplan=export_plan)
    factories.ExportPlanActionsFactory.create(companyexportplan=export_plan)

    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})

    data = {'target_markets': export_plan.target_markets + [{'country': 'Australia'}]}

    response = authed_client.patch(url, data, format='json')
    export_plan.refresh_from_db()

    assert response.status_code == http.client.OK

    country_market_data = {
        'country': 'Mexico',
        'last_year_data': {'import_value': {'year': 2019, 'trade_value': 100}},
        'easeofdoingbusiness': {'total': 1, 'year_2019': 20, 'country_code': 'AUS', 'country_name': 'Australia'},
        'corruption_perceptions_index': {
            'rank': 21,
            'country_code': 'AUS',
            'country_name': 'Australia',
            'cpi_score': 24,
        },
        'historical_import_data': {
            'historical_trade_value_all': {'2016': 350, '2017': 350, '2018': 350},
            'historical_trade_value_partner': {'2016': 50, '2017': 100, '2018': 200},
        },
        'timezone': 'America/Mexico_City',
        'utz_offset': '-0500',
        'world_economic_outlook_data': [{'year_2019': 20, 'country_code': 'AUS', 'country_name': 'Australia'}],
        'cia_factbook_data': {'capital': 'London', 'currency': 'GBP', 'population': '60m'},
    }
    # We can't compare actual time offsets as these vary over time
    country_market_data['utz_offset'] = export_plan.target_markets[0]['utz_offset']
    assert export_plan.target_markets[0] == country_market_data
    country_market_data['country'] = 'Australia'
    country_market_data['utz_offset'] = export_plan.target_markets[1]['utz_offset']
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
        {'is_reminders_on': False, 'due_date': '2020-01-02'},
    ]
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})
    data = {'export_plan_actions': actions}

    response = authed_client.patch(url, data, format='json')

    export_plan.refresh_from_db()
    assert response.status_code == http.client.OK
    export_plan_actions = export_plan.export_plan_actions.all()
    assert len(export_plan_actions) == 2
    assert export_plan_actions[0].is_reminders_on is True
    assert export_plan_actions[0].due_date == date(2020, 1, 1)
    assert export_plan_actions[1].is_reminders_on is False
    assert export_plan_actions[1].due_date == date(2020, 1, 2)


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
    my_objective = export_plan.company_objectives.last()

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


@pytest.mark.django_db
def test_route_to_market_update(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    route_to_market = export_plan.route_to_markets.all()[0]
    url = reverse('export-plan-route-to-markets-detail-update', kwargs={'pk': route_to_market.pk})

    data = {'route': choices.MARKET_ROUTE_CHOICES[0][0]}

    response = authed_client.patch(url, data, format='json')
    route_to_market.refresh_from_db()

    assert response.status_code == http.client.OK
    assert route_to_market.route == choices.MARKET_ROUTE_CHOICES[0][0]


@pytest.mark.django_db
def test_route_to_market_retrieve(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    route_to_market = export_plan.route_to_markets.all()[0]
    url = reverse('export-plan-route-to-markets-detail-update', kwargs={'pk': route_to_market.pk})

    response = authed_client.get(url)
    data = response.json()
    assert response.status_code == http.client.OK
    assert route_to_market.pk == data['pk']
    assert route_to_market.route == data['route']
    assert route_to_market.promote == data['promote']
    assert route_to_market.market_promotional_channel == data['market_promotional_channel']


@pytest.mark.django_db
def test_route_to_market_create(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-route-to-markets-list-create')

    data = {
        'companyexportplan': export_plan.id,
        'route': choices.MARKET_ROUTE_CHOICES[0][0],
        'promote': choices.PRODUCT_PROMOTIONAL_CHOICES[0][0],
        'market_promotional_channel': 'facebook',
    }

    response = authed_client.post(url, data)

    data = response.json()

    assert response.status_code == http.client.CREATED
    export_plan.refresh_from_db()
    assert export_plan.route_to_markets.all().count() == 2
    route_to_market = export_plan.route_to_markets.last()
    assert route_to_market.pk == data['pk']
    assert route_to_market.route == data['route']
    assert route_to_market.promote == data['promote']
    assert route_to_market.market_promotional_channel == data['market_promotional_channel']


@pytest.mark.django_db
def test_route_to_market_delete(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    route_to_market = export_plan.route_to_markets.all()[0]
    url = reverse('export-plan-route-to-markets-detail-update', kwargs={'pk': route_to_market.pk})

    response = authed_client.delete(url)
    assert response.status_code == http.client.NO_CONTENT
    assert not export_plan.route_to_markets.all()


@pytest.mark.django_db
def test_target_market_doc_update(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    target_market_docs = export_plan.target_market_documents.all()[0]
    url = reverse('export-plan-target-market-documents-detail-update', kwargs={'pk': target_market_docs.pk})

    data = {'document_name': 'update me'}
    response = authed_client.patch(url, data, format='json')
    target_market_docs.refresh_from_db()

    assert response.status_code == http.client.OK
    assert target_market_docs.document_name == data['document_name']


@pytest.mark.django_db
def test_target_market_doc_retrieve(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    target_market_docs = export_plan.target_market_documents.all()[0]
    url = reverse('export-plan-target-market-documents-detail-update', kwargs={'pk': target_market_docs.pk})
    response = authed_client.get(url)
    data = response.json()
    assert response.status_code == http.client.OK
    assert target_market_docs.pk == data['pk']
    assert target_market_docs.document_name == data['document_name']
    assert target_market_docs.note == data['note']


@pytest.mark.django_db
def test_target_market_doc_create(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-target-market-documents-list-create')

    data = {
        'companyexportplan': export_plan.id,
        'document_name': 'name update',
        'note': 'new notes',
    }

    response = authed_client.post(url, data)

    data = response.json()

    assert response.status_code == http.client.CREATED
    export_plan.refresh_from_db()
    assert export_plan.target_market_documents.all().count() == 2
    adaptation_docs = export_plan.target_market_documents.last()
    assert adaptation_docs.pk == data['pk']
    assert adaptation_docs.document_name == data['document_name']
    assert adaptation_docs.note == data['note']


@pytest.mark.django_db
def test_adaptation_target_market_doc_delete(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    target_market_docs = export_plan.target_market_documents.all()[0]
    url = reverse('export-plan-target-market-documents-detail-update', kwargs={'pk': target_market_docs.pk})

    response = authed_client.delete(url)
    assert response.status_code == http.client.NO_CONTENT
    assert not export_plan.target_market_documents.all()


@pytest.mark.django_db
def test_export_plan_update_json_new_to_partial(authed_client, authed_supplier):
    export_plan = factories.CompanyExportPlanFactory.create(about_your_business={})

    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})
    response = authed_client.get(url)

    assert response.status_code == 200
    assert response.json()['about_your_business'] == {}

    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})
    data = {'about_your_business': {'Location': 'London', 'story': 'new brand'}}
    response = authed_client.patch(url, data, format='json')
    assert response.status_code == 200
    assert response.json()['about_your_business'] == data['about_your_business']
    # Update just single field
    data = {'about_your_business': {'Location': 'New York'}}
    response = authed_client.patch(url, data, format='json')
    assert response.status_code == 200
    assert response.json()['about_your_business'] == {'Location': 'New York', 'story': 'new brand'}

    # Add new field
    data = {'about_your_business': {'New': 'New Item'}}
    response = authed_client.patch(url, data, format='json')
    assert response.status_code == 200
    assert response.json()['about_your_business'] == {'Location': 'New York', 'story': 'new brand', 'New': 'New Item'}


@pytest.mark.django_db
def test_export_plan_update_json_new_to_partial_inner_dict(authed_client, authed_supplier):
    export_plan = factories.CompanyExportPlanFactory.create(ui_progress={'section-a': {'opt-a': 'A', 'opt-b': 'B'}})

    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})
    response = authed_client.get(url)
    assert response.status_code == 200
    assert response.json()['ui_progress'] == {'section-a': {'opt-a': 'A', 'opt-b': 'B'}}

    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})
    data = {'ui_progress': {'section-a': {'opt-a': 'A', 'opt-b': 'b2'}}}
    response = authed_client.patch(url, data, format='json')
    assert response.status_code == 200
    assert response.json()['ui_progress'] == {'section-a': {'opt-a': 'A', 'opt-b': 'b2'}}

    # add a new section
    data = {'ui_progress': {'section-b': {'opt-c': 'C'}}}
    response = authed_client.patch(url, data, format='json')
    assert response.status_code == 200
    assert response.json()['ui_progress'] == {'section-a': {'opt-a': 'A', 'opt-b': 'b2'}, 'section-b': {'opt-c': 'C'}}

    # add a new option
    data = {'ui_progress': {'section-b': {'opt-d': 'D'}}}
    response = authed_client.patch(url, data, format='json')
    assert response.status_code == 200
    assert response.json()['ui_progress'] == {
        'section-a': {'opt-a': 'A', 'opt-b': 'b2'},
        'section-b': {'opt-c': 'C', 'opt-d': 'D'},
    }


@pytest.mark.django_db
def test_export_plan_update_non_json_new_to_partial(authed_client, authed_supplier):
    export_plan = factories.CompanyExportPlanFactory.create(resource_needed='')

    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})
    response = authed_client.get(url)

    assert response.status_code == 200
    assert response.json()['resource_needed'] == ''

    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})
    data = {'resource_needed': 'New resource'}
    response = authed_client.patch(url, data, format='json')
    assert response.status_code == 200
    assert response.json()['resource_needed'] == 'New resource'
    # Update
    data = {'resource_needed': 'Old resource'}
    response = authed_client.patch(url, data, format='json')
    assert response.status_code == 200
    assert response.json()['resource_needed'] == 'Old resource'


@pytest.mark.django_db
def test_funding_credit_options_update(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    funding_credit_option = export_plan.funding_credit_options.all()[0]
    url = reverse('export-plan-funding-credit-options-detail-update', kwargs={'pk': funding_credit_option.pk})

    data = {'amount': '12.34'}
    response = authed_client.patch(url, data, format='json')
    funding_credit_option.refresh_from_db()

    assert response.status_code == http.client.OK
    assert funding_credit_option.amount == float(data['amount'])


@pytest.mark.django_db
def test_funding_credit_options_retrieve(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    funding_credit_option = export_plan.funding_credit_options.all()[0]
    url = reverse('export-plan-funding-credit-options-detail-update', kwargs={'pk': funding_credit_option.pk})
    response = authed_client.get(url)
    data = response.json()
    assert response.status_code == http.client.OK
    assert funding_credit_option.pk == data['pk']
    assert funding_credit_option.amount == data['amount']
    assert funding_credit_option.funding_option == data['funding_option']


@pytest.mark.django_db
def test_funding_credit_options_create(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-funding-credit-options-list-create')

    data = {
        'companyexportplan': export_plan.id,
        'funding_option': 'GOVERNMENT',
        'amount': '55.23',
    }

    response = authed_client.post(url, data)
    data = response.json()

    assert response.status_code == http.client.CREATED
    export_plan.refresh_from_db()
    assert export_plan.funding_credit_options.all().count() == 2
    funding_credit_option = export_plan.funding_credit_options.last()
    assert funding_credit_option.pk == data['pk']
    assert funding_credit_option.amount == data['amount']
    assert funding_credit_option.funding_option == data['funding_option']


@pytest.mark.django_db
def test_funding_credit_options_delete(authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    target_market_docs = export_plan.funding_credit_options.all()[0]

    url = reverse('export-plan-funding-credit-options-detail-update', kwargs={'pk': target_market_docs.pk})

    response = authed_client.delete(url)
    assert response.status_code == http.client.NO_CONTENT
    assert not export_plan.funding_credit_options.all()


@pytest.mark.parametrize(
    'model_class, property_name, create_data',
    [
        [models.FundingCreditOptions, 'funding_credit_options', {'funding_option': 'GOVERNMENT', 'amount': 55.23}],
        [
            models.CompanyObjectives,
            'company_objectives',
            {
                'description': 'newly created',
                'planned_reviews': 'None planned',
            },
        ],
        [
            models.RouteToMarkets,
            'route_to_markets',
            {
                'route': choices.MARKET_ROUTE_CHOICES[0][0],
                'promote': choices.PRODUCT_PROMOTIONAL_CHOICES[0][0],
                'market_promotional_channel': 'facebook',
            },
        ],
        [
            models.TargetMarketDocuments,
            'target_market_documents',
            {'document_name': 'name update', 'note': 'new notes'},
        ],
        [models.ExportPlanActions, 'export_plan_actions', {'action_type': 'TARGET_MARKETS', 'is_reminders_on': True}],
        [models.BusinessTrips, 'business_trips', {'note': 'I just got created'}],
        [
            models.BusinessTrips,
            'business_trips',
            {'risk': 'new risk', 'contingency_plan': 'contingency', 'risk_likelihood': 'RARE', 'risk_impact': 'SEVERE'},
        ],
    ],
)
@pytest.mark.django_db
def test_export_plan_model_create(model_class, property_name, create_data, authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    url = reverse('export-plan-model-object-list-create')

    create_data['companyexportplan'] = export_plan.id
    create_data['model_name'] = model_class.__name__

    response = authed_client.post(url, create_data)
    data_returned = response.json()
    assert response.status_code == http.client.CREATED

    export_plan.refresh_from_db()

    assert data_returned.pop('companyexportplan') == export_plan.id
    assert getattr(export_plan, property_name).all().count() == 2
    object_created = getattr(export_plan, property_name).last()

    for k, v in data_returned.items():
        assert getattr(object_created, k) == v


@pytest.mark.parametrize(
    'model_class, property_name',
    [
        [models.FundingCreditOptions, 'funding_credit_options'],
        [models.CompanyObjectives, 'company_objectives'],
        [models.RouteToMarkets, 'route_to_markets'],
        [models.TargetMarketDocuments, 'target_market_documents'],
        [models.ExportPlanActions, 'export_plan_actions'],
        [models.BusinessTrips, 'business_trips'],
        [models.BusinessRisks, 'business_risks'],
    ],
)
@pytest.mark.django_db
def test_export_plan_model_retrieve(model_class, property_name, authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()

    model_object = getattr(export_plan, property_name).all()[0]

    # lower model name is deliberate to test that it's not case sensitive
    url = reverse(
        'export-plan-model-object-detail', kwargs={'pk': model_object.pk, 'model_name': model_class.__name__.lower()}
    )
    response = authed_client.get(url)

    model_data = response.json()
    assert response.status_code == http.client.OK
    assert len(model_data) > 1
    assert model_data.pop('companyexportplan') == export_plan.id
    for k, v in model_data.items():
        assert getattr(model_object, k) == v


@pytest.mark.parametrize(
    'model_class, property_name, data_update',
    [
        [models.FundingCreditOptions, 'funding_credit_options', {'amount': 12.34}],
        [models.CompanyObjectives, 'company_objectives', {'description': 'updated now'}],
        [models.RouteToMarkets, 'route_to_markets', {'route': choices.MARKET_ROUTE_CHOICES[0][0]}],
        [models.TargetMarketDocuments, 'target_market_documents', {'document_name': 'update me'}],
        [models.ExportPlanActions, 'export_plan_actions', {'is_reminders_on': True}],
        [models.BusinessTrips, 'business_trips', {'note': 'update my trip'}],
        [models.BusinessRisks, 'business_risks', {'risk': 'update my risk'}],
    ],
)
@pytest.mark.django_db
def test_export_plan_model_update(model_class, property_name, data_update, authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    attribute_updated = list(data_update.keys())[0]
    data_update['model_name'] = model_class.__name__
    model_object = getattr(export_plan, property_name).all()[0]
    url = reverse('export-plan-model-object-update-delete', kwargs={'pk': model_object.pk})

    response = authed_client.patch(url, data_update, format='json')
    model_object.refresh_from_db()

    assert response.status_code == http.client.OK
    assert getattr(model_object, attribute_updated) == data_update[attribute_updated]


@pytest.mark.parametrize(
    'model_class, property_name',
    [
        [models.FundingCreditOptions, 'funding_credit_options'],
        [models.CompanyObjectives, 'company_objectives'],
        [models.RouteToMarkets, 'route_to_markets'],
        [models.TargetMarketDocuments, 'target_market_documents'],
        [models.ExportPlanActions, 'export_plan_actions'],
        [models.BusinessTrips, 'business_trips'],
        [models.BusinessRisks, 'business_risks'],
    ],
)
@pytest.mark.django_db
def test_export_plan_model_delete(model_class, property_name, authed_client, authed_supplier, export_plan):
    authed_supplier.sso_id = export_plan.sso_id
    authed_supplier.company = export_plan.company
    authed_supplier.save()
    model_object = getattr(export_plan, property_name).all()[0]

    # Upper model name is deliberate to test that it's not case sensitive
    data = {'model_name': model_class.__name__.upper()}
    url = reverse('export-plan-model-object-update-delete', kwargs={'pk': model_object.pk})
    response = authed_client.delete(url, data, format='json')

    assert response.status_code == http.client.NO_CONTENT
    assert not getattr(export_plan, property_name).all()
