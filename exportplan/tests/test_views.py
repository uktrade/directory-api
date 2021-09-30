import http
from unittest import mock

import pytest
from directory_constants import choices
from django.core.files import File
from django.urls import reverse

from company.tests.factories import CompanyFactory
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
    }


@pytest.fixture
def export_plan(authed_supplier):
    export_plan = factories.CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)
    factories.CompanyObjectivesFactory.create(companyexportplan=export_plan)
    factories.RouteToMarketsFactory.create(companyexportplan=export_plan)
    factories.TargetMarketDocumentsFactory.create(companyexportplan=export_plan)
    factories.FundingCreditOptionsFactory.create(companyexportplan=export_plan)
    factories.BusinessTripsFactory.create(companyexportplan=export_plan)
    factories.BusinessRiskFactory.create(companyexportplan=export_plan)
    return export_plan


@pytest.mark.django_db
def test_export_plan_retrieve(authed_client, export_plan):
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
        'marketing_approach': export_plan.marketing_approach,
        'target_markets_research': export_plan.target_markets_research,
        'adaptation_target_market': export_plan.adaptation_target_market,
        'direct_costs': export_plan.direct_costs,
        'overhead_costs': export_plan.overhead_costs,
        'total_cost_and_price': export_plan.total_cost_and_price,
        'company_objectives': [
            {
                'companyexportplan': export_plan.id,
                'description': 'export 5k cases of wine',
                'planned_reviews': 'None planned',
                'owner': None,
                'start_month': None,
                'start_year': None,
                'end_month': None,
                'end_year': None,
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
def test_export_plan_retrieve_403(authed_client, export_plan):
    non_owner_exportplan = factories.CompanyExportPlanFactory.create(sso_id=export_plan.sso_id + 1)
    url = reverse('export-plan-detail-update', kwargs={'pk': non_owner_exportplan.pk})
    response = authed_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_export_plan_retrieve_not_found(authed_client, export_plan):
    url = reverse('export-plan-detail-update', kwargs={'pk': 10000})
    with pytest.raises(models.CompanyExportPlan.DoesNotExist):
        authed_client.get(url)


@pytest.mark.django_db
def test_export_plan_update(authed_client, export_plan):
    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})

    data = {'export_commodity_codes': [{'commodity_name': 'vodka', 'commodity_code': '104.2402.123'}]}
    assert export_plan.export_commodity_codes != data['export_commodity_codes']

    response = authed_client.patch(url, data, format='json')
    assert response.status_code == http.client.OK
    export_plan.refresh_from_db()
    assert export_plan.export_commodity_codes == data['export_commodity_codes']


@pytest.mark.django_db
def test_export_plan_update_403(authed_client, export_plan):
    non_owner_exportplan = factories.CompanyExportPlanFactory.create(sso_id=export_plan.sso_id + 1)
    url = reverse('export-plan-detail-update', kwargs={'pk': non_owner_exportplan.pk})

    data = {'export_commodity_codes': [{'commodity_name': 'vodka', 'commodity_code': '104.2402.123'}]}
    response = authed_client.patch(url, data, format='json')
    assert response.status_code == 403


@pytest.mark.django_db
def test_export_plan_list_detail(authed_client, authed_supplier):
    factories.CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)
    factories.CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id)
    factories.CompanyExportPlanFactory.create(sso_id=authed_supplier.sso_id + 1)

    response = authed_client.get(reverse('export-plan-detail-list'))
    assert list(response.json()[0].keys()) == [
        'pk',
        'created',
        'ui_progress',
        'export_countries',
        'export_commodity_codes',
    ]
    assert response.status_code == 200

    assert len(response.json()) == 2


@pytest.mark.django_db
def test_export_plan_create(authed_client, authed_supplier):

    url = reverse('export-plan-create')

    data = {
        'export_commodity_codes': [{'commodity_name': 'gin', 'commodity_code': '101.2002.123'}],
        'export_countries': [{'country_name': 'China', 'country_iso2_code': 'CN'}],
    }
    response = authed_client.post(url, data, format='json')

    assert response.status_code == 201
    export_plan_db = models.CompanyExportPlan.objects.last()
    created_export_plan = response.json()

    assert export_plan_db.sso_id == authed_supplier.sso_id
    assert export_plan_db.export_commodity_codes == created_export_plan['export_commodity_codes']
    assert export_plan_db.export_countries == created_export_plan['export_countries']


@pytest.mark.django_db
def test_export_plan_update_json_new_to_partial(authed_client, authed_supplier):
    export_plan = factories.CompanyExportPlanFactory.create(about_your_business={}, sso_id=authed_supplier.sso_id)
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
    export_plan = factories.CompanyExportPlanFactory.create(
        ui_progress={'section-a': {'opt-a': 'A', 'opt-b': 'B'}}, sso_id=authed_supplier.sso_id
    )
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
    export_plan = factories.CompanyExportPlanFactory.create(adaptation_target_market={}, sso_id=authed_supplier.sso_id)

    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})
    response = authed_client.get(url)

    assert response.status_code == 200
    assert response.json()['adaptation_target_market'] == {}

    url = reverse('export-plan-detail-update', kwargs={'pk': export_plan.pk})
    data = {'adaptation_target_market': {'labelling': 'auto', 'size': '6l'}}
    response = authed_client.patch(url, data, format='json')
    assert response.status_code == 200
    assert response.json()['adaptation_target_market'] == {'labelling': 'auto', 'size': '6l'}
    # Update
    data = {'adaptation_target_market': {'labelling': 'manual'}}
    response = authed_client.patch(url, data, format='json')
    assert response.status_code == 200
    assert response.json()['adaptation_target_market'] == {'labelling': 'manual', 'size': '6l'}


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
        [models.BusinessTrips, 'business_trips', {'note': 'I just got created'}],
        [
            models.BusinessTrips,
            'business_trips',
            {'risk': 'new risk', 'contingency_plan': 'contingency', 'risk_likelihood': 'RARE', 'risk_impact': 'SEVERE'},
        ],
    ],
)
@pytest.mark.django_db
def test_export_plan_model_create(model_class, property_name, create_data, authed_client, export_plan):
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
        [models.BusinessTrips, 'business_trips'],
        [models.BusinessRisks, 'business_risks'],
    ],
)
@pytest.mark.django_db
def test_export_plan_model_retrieve(model_class, property_name, authed_client, export_plan):

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
        [models.BusinessTrips, 'business_trips', {'note': 'update my trip'}],
        [models.BusinessRisks, 'business_risks', {'risk': 'update my risk'}],
    ],
)
@pytest.mark.django_db
def test_export_plan_model_update(model_class, property_name, data_update, authed_client, export_plan):

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
        [models.BusinessTrips, 'business_trips'],
        [models.BusinessRisks, 'business_risks'],
    ],
)
@pytest.mark.django_db
def test_export_plan_model_delete(model_class, property_name, authed_client, export_plan):

    model_object = getattr(export_plan, property_name).all()[0]

    # Upper model name is deliberate to test that it's not case sensitive
    data = {'model_name': model_class.__name__.upper()}
    url = reverse('export-plan-model-object-update-delete', kwargs={'pk': model_object.pk})
    response = authed_client.delete(url, data, format='json')

    assert response.status_code == http.client.NO_CONTENT
    assert not getattr(export_plan, property_name).all()


@pytest.mark.django_db
def test_export_plan_pdf_upload(authed_client, export_plan):
    mock_file = mock.Mock(spec=File)
    url = reverse('export-plan-pdf-upload')

    data = {'companyexportplan': export_plan.id, 'pdf_file': mock_file}

    response = authed_client.post(url, data)
    assert response.status_code == 201
    export_plan_upload = models.ExportplanDownloads.objects.last()
    assert export_plan_upload.companyexportplan.id == export_plan.id
    assert export_plan_upload.pdf_file is not None


@pytest.mark.django_db
def test_export_plan_pdf_upload_403(authed_client, export_plan):
    mock_file = mock.Mock(spec=File)
    url = reverse('export-plan-pdf-upload')
    non_owner_exportplan = factories.CompanyExportPlanFactory.create(sso_id=export_plan.sso_id + 1)
    data = {'companyexportplan': non_owner_exportplan.id, 'pdf_file': mock_file}

    response = authed_client.post(url, data)
    assert response.status_code == 403
