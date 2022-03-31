import datetime
from unittest import mock

import mohawk
import pytest
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from company.tests.factories import CompanyFactory
from exportplan.tests.factories import CompanyExportPlanFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def activities_url():
    return 'http://testserver' + reverse('activity-stream:activity-stream')


@pytest.fixture
def companies_url():
    return 'http://testserver' + reverse('activity-stream:activity-stream-companies')


@pytest.fixture
def exportplan_url():
    return 'http://testserver' + reverse('activity-stream:activity-stream-export-plans')


@pytest.fixture
def _url_incorrect_domain():
    return 'http://incorrect' + reverse('activity-stream:activity-stream')


@pytest.fixture
def _url_incorrect_path():
    return 'http://testserver' + reverse('activity-stream:activity-stream') + 'incorrect/'


def _empty_collection():
    return {
        '@context': [
            'https://www.w3.org/ns/activitystreams',
            {
                'dit': 'https://www.trade.gov.uk/ns/activitystreams/v1',
            },
        ],
        'type': 'Collection',
        'orderedItems': [],
    }


def _auth_sender(url, key_id='some-id', secret_key='some-secret', method='GET', content='', content_type=''):
    credentials = {
        'id': key_id,
        'key': secret_key,
        'algorithm': 'sha256',
    }
    return mohawk.Sender(
        credentials,
        url,
        method,
        content=content,
        content_type=content_type,
    )


def get_companies_house_number(activity):
    """Returns the companies house number of an activity"""
    return activity['object']['attributedTo']['dit:companiesHouseNumber']


def get_company_name(activity):
    """Returns the company name of an activity"""
    return activity['object']['attributedTo']['name']


def get_company_id(activity):
    return activity['object']['attributedTo']['id']


@pytest.mark.django_db
def test_empty_object_returned_with_authentication(api_client, activities_url):
    """If the Authorization and X-Forwarded-For headers are correct, then
    the correct, and authentic, data is returned
    """
    sender = _auth_sender(activities_url)
    response = api_client.get(
        activities_url,
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == _empty_collection()

    # Just asserting that accept_response doesn't raise is a bit weak,
    # so we also assert that it raises if the header, content, or
    # content_type are incorrect
    sender.accept_response(
        response_header=response['Server-Authorization'],
        content=response.content,
        content_type=response['Content-Type'],
    )
    with pytest.raises(mohawk.exc.MacMismatch):
        sender.accept_response(
            response_header=response['Server-Authorization'] + 'incorrect',
            content=response.content,
            content_type=response['Content-Type'],
        )
    with pytest.raises(mohawk.exc.MisComputedContentHash):
        sender.accept_response(
            response_header=response['Server-Authorization'],
            content='incorrect',
            content_type=response['Content-Type'],
        )
    with pytest.raises(mohawk.exc.MisComputedContentHash):
        sender.accept_response(
            response_header=response['Server-Authorization'],
            content=response.content,
            content_type='incorrect',
        )


@pytest.mark.django_db
def test_if_never_verified_not_in_stream(api_client, activities_url):
    """If the company never verified, then it's not in the activity stream"""

    with freeze_time('2012-01-14 12:00:02'):
        CompanyFactory()

    sender = _auth_sender(activities_url)
    response = api_client.get(
        activities_url,
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        '@context': [
            'https://www.w3.org/ns/activitystreams',
            {
                'dit': 'https://www.trade.gov.uk/ns/activitystreams/v1',
            },
        ],
        'type': 'Collection',
        'orderedItems': [],
        'next': 'http://testserver/activity-stream/?after=1326542402.0_3',
    }


@pytest.mark.django_db
def test_if_verified_with_code_in_stream_in_date_then_seq_order(api_client, activities_url):
    """If the company verified_with_code, then it's in the activity stream"""

    CompanyFactory(number=10000000)

    with freeze_time('2012-01-14 12:00:02'):
        company_a = CompanyFactory(number=10000003, name='a', verified_with_code=True)

    with freeze_time('2012-01-14 12:00:02'):
        company_b = CompanyFactory(number=10000002, name='b', verified_with_code=True)

    with freeze_time('2012-01-14 12:00:01'):
        company_c = CompanyFactory(number=10000001, name='c', verified_with_code=True)

    sender = _auth_sender(activities_url)
    response = api_client.get(
        activities_url,
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    items = response.json()['orderedItems']

    id_prefix = 'dit:directory:Company:'

    assert len(items) == 3
    assert items[0]['published'] == '2012-01-14T12:00:01+00:00'
    assert get_companies_house_number(items[0]) == '10000001'
    assert get_company_name(items[0]) == 'c'
    assert get_company_id(items[0]) == id_prefix + str(company_c.id)
    assert items[1]['published'] == '2012-01-14T12:00:02+00:00'
    assert get_companies_house_number(items[1]) == '10000003'
    assert get_company_name(items[1]) == 'a'
    assert get_company_id(items[1]) == id_prefix + str(company_a.id)
    assert items[2]['published'] == '2012-01-14T12:00:02+00:00'
    assert get_companies_house_number(items[2]) == '10000002'
    assert get_company_name(items[2]) == 'b'
    assert get_company_id(items[2]) == id_prefix + str(company_b.id)


@pytest.mark.django_db
def test_if_verified_with_code_then_deleted_not_in_stream(api_client, activities_url):
    """If the company verified_with_code, then deleted, then not in the stream

    This may need to be changed, but this confirms/documents behaviour, and
    ensures that the endpoint doesn't break in this case
    """

    to_delete = CompanyFactory(number=10000001, verified_with_code=True)
    CompanyFactory(number=10000002, verified_with_code=True)

    to_delete.delete()

    sender = _auth_sender(activities_url)
    response = api_client.get(
        activities_url,
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    items = response.json()['orderedItems']

    assert len(items) == 1
    assert get_companies_house_number(items[0]) == '10000002'


@pytest.mark.django_db
def test_if_verified_with_companies_house_oauth2_in_stream(api_client, activities_url):
    """If the company verified_with_companies_house_oauth2, then it's n the
    activity stream
    """

    CompanyFactory(number=10000000, verified_with_companies_house_oauth2=True)

    sender = _auth_sender(activities_url)
    response = api_client.get(
        activities_url,
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    items = response.json()['orderedItems']

    assert len(items) == 1
    assert get_companies_house_number(items[0]) == '10000000'


@pytest.mark.django_db
def test_if_verified_with_preverified_enrolment_in_stream(api_client, activities_url):
    """If the company verified_with_preverified_enrolment, then it's in the
    activity stream
    """

    CompanyFactory(number=10000000, verified_with_preverified_enrolment=True)

    sender = _auth_sender(activities_url)
    response = api_client.get(
        activities_url,
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    items = response.json()['orderedItems']

    assert len(items) == 1
    assert get_companies_house_number(items[0]) == '10000000'


@pytest.mark.django_db
def test_pagination(api_client, django_assert_num_queries, activities_url):
    """The requests are paginated, ending on a page without a next key"""

    with freeze_time('2012-01-14 12:00:02'):
        for i in range(0, 250):
            CompanyFactory(number=10000000 + i, verified_with_preverified_enrolment=True)

    with freeze_time('2012-01-14 12:00:01'):
        for i in range(250, 501):
            CompanyFactory(number=10000000 + i, verified_with_preverified_enrolment=True)

    items = []
    next_url = activities_url
    num_pages = 0

    with django_assert_num_queries(9):
        while next_url:
            num_pages += 1
            sender = _auth_sender(next_url)
            response = api_client.get(
                next_url,
                content_type='',
                HTTP_AUTHORIZATION=sender.request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
            )
            response_json = response.json()
            items += response_json['orderedItems']
            next_url = response_json['next'] if 'next' in response_json else None

    assert num_pages == 5
    assert len(items) == 501
    assert len(set([item['id'] for item in items])) == 501
    assert get_companies_house_number(items[500]) == '10000249'


@pytest.mark.django_db
def test_if_61_seconds_in_past_401_returned(api_client, activities_url):
    """If the Authorization header is generated 61 seconds in the past, then a
    401 is returned
    """
    past = datetime.datetime.now() - datetime.timedelta(seconds=61)
    with freeze_time(past):
        auth = _auth_sender(activities_url).request_header
    response = api_client.get(
        activities_url,
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error = {'detail': 'Incorrect authentication credentials.'}
    assert response.json() == error


def _expected_company_response(company):
    return {
        'id': f'dit:directory:Company:{company.id}:Update',
        'published': company.date_published.strftime('%Y-%m-%d'),
        'generator': {'type': 'Application', 'name': 'dit:directory'},
        'object': {
            'id': f'dit:directory:Company:{company.id}',
            'type': 'dit:directory:Company',
            'dit:directory:Company:address_line_1': company.address_line_1,
            'dit:directory:Company:address_line_2': company.address_line_2,
            'dit:directory:Company:company_type': company.company_type,
            'dit:directory:Company:country': company.country,
            'dit:directory:Company:created': company.created.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'dit:directory:Company:date_of_creation': company.date_of_creation,
            'dit:directory:Company:description': company.description,
            'dit:directory:Company:email_address': company.email_address,
            'dit:directory:Company:email_full_name': company.email_full_name,
            'dit:directory:Company:employees': company.employees,
            'dit:directory:Company:facebook_url': company.facebook_url,
            'dit:directory:Company:has_exported_before': company.has_exported_before,
            'dit:directory:Company:id': company.id,
            'dit:directory:Company:is_exporting_goods': company.is_exporting_goods,
            'dit:directory:Company:is_exporting_services': company.is_exporting_services,
            'dit:directory:Company:is_published': company.is_published,
            'dit:directory:Company:is_publishable': company.is_publishable,
            'dit:directory:Company:is_published_investment_support_directory': (
                company.is_published_investment_support_directory
            ),
            'dit:directory:Company:is_published_find_a_supplier': company.is_published_find_a_supplier,
            'dit:directory:Company:is_registration_letter_sent': company.is_registration_letter_sent,
            'dit:directory:Company:is_verification_letter_sent': company.is_verification_letter_sent,
            'dit:directory:Company:is_identity_check_message_sent': company.is_identity_check_message_sent,
            'dit:directory:Company:keywords': company.keywords,
            'dit:directory:Company:linkedin_url': company.linkedin_url,
            'dit:directory:Company:locality': company.locality,
            'dit:directory:Company:mobile_number': company.mobile_number,
            'dit:directory:Company:modified': company.modified.strftime('%Y-%m-%dT%H:%M:%SZ'),
            'dit:directory:Company:name': company.name,
            'dit:directory:Company:number': company.number,
            'dit:directory:Company:po_box': company.po_box,
            'dit:directory:Company:postal_code': company.postal_code,
            'dit:directory:Company:postal_full_name': company.postal_full_name,
            'dit:directory:Company:sectors': company.sectors,
            'dit:directory:Company:hs_codes': company.hs_codes,
            'dit:directory:Company:slug': company.slug,
            'dit:directory:Company:summary': company.summary,
            'dit:directory:Company:twitter_url': company.twitter_url,
            'dit:directory:Company:website': company.website,
            'dit:directory:Company:verified_with_code': company.verified_with_code,
            'dit:directory:Company:verified_with_preverified_enrolment': company.verified_with_preverified_enrolment,
            'dit:directory:Company:verified_with_companies_house_oauth2': company.verified_with_companies_house_oauth2,
            'dit:directory:Company:verified_with_identity_check': company.verified_with_identity_check,
            'dit:directory:Company:is_verified': company.is_verified,
            'dit:directory:Company:export_destinations': [],
            'dit:directory:Company:export_destinations_other': company.export_destinations_other,
            'dit:directory:Company:is_uk_isd_company': company.is_uk_isd_company,
            'dit:directory:Company:expertise_industries': company.expertise_industries,
            'dit:directory:Company:expertise_regions': company.expertise_regions,
            'dit:directory:Company:expertise_countries': company.expertise_countries,
            'dit:directory:Company:expertise_languages': company.expertise_languages,
            'dit:directory:Company:expertise_products_services': {
                'other': ['Regulatory', 'Finance', 'IT'],
                'Finance': ['Insurance'],
            },
            'dit:directory:Company:date_published': company.date_published,
        },
    }


def _expected_export_plan_response(export_plan):
    modified = export_plan.modified.isoformat()
    exportplan_id = export_plan.id
    return [
        {
            'id': f'dit:directory:ExportPlan:{exportplan_id}:Update',
            'modified': modified,
            'generator': {
                'type': 'Application',
                'name': 'dit:directory',
            },
            'object': {
                'id': f'dit:directory:ExportPlan:{exportplan_id}',
                'type': 'dit:directory:ExportPlan',
                'dit:directory:ExportPlan:Section': 'export_countries',
                'dit:directory:ExportPlan:Question': 'country_name',
                'dit:directory:ExportPlan:Response': 'China',
            },
        },
        {
            'id': f'dit:directory:ExportPlan:{exportplan_id}:Update',
            'modified': modified,
            'generator': {
                'type': 'Application',
                'name': 'dit:directory',
            },
            'object': {
                'id': f'dit:directory:ExportPlan:{exportplan_id}',
                'type': 'dit:directory:ExportPlan',
                'dit:directory:ExportPlan:Section': 'export_countries',
                'dit:directory:ExportPlan:Question': 'country_iso2_code',
                'dit:directory:ExportPlan:Response': 'CN',
            },
        },
        {
            'id': f'dit:directory:ExportPlan:{exportplan_id}:Update',
            'modified': modified,
            'generator': {
                'type': 'Application',
                'name': 'dit:directory',
            },
            'object': {
                'id': f'dit:directory:ExportPlan:{exportplan_id}',
                'type': 'dit:directory:ExportPlan',
                'dit:directory:ExportPlan:Section': 'export_commodity_codes',
                'dit:directory:ExportPlan:Question': 'commodity_code',
                'dit:directory:ExportPlan:Response': '101.2002.123',
            },
        },
        {
            'id': f'dit:directory:ExportPlan:{exportplan_id}:Update',
            'modified': modified,
            'generator': {
                'type': 'Application',
                'name': 'dit:directory',
            },
            'object': {
                'id': f'dit:directory:ExportPlan:{exportplan_id}',
                'type': 'dit:directory:ExportPlan',
                'dit:directory:ExportPlan:Section': 'export_commodity_codes',
                'dit:directory:ExportPlan:Question': 'commodity_name',
                'dit:directory:ExportPlan:Response': 'gin',
            },
        },
        {
            'id': f'dit:directory:ExportPlan:{exportplan_id}:Update',
            'modified': modified,
            'generator': {
                'type': 'Application',
                'name': 'dit:directory',
            },
            'object': {
                'id': f'dit:directory:ExportPlan:{exportplan_id}',
                'type': 'dit:directory:ExportPlan',
                'dit:directory:ExportPlan:Section': 'about_your_business',
                'dit:directory:ExportPlan:Question': 'q_1',
                'dit:directory:ExportPlan:Response': 'response 1',
            },
        },
        {
            'id': f'dit:directory:ExportPlan:{exportplan_id}:Update',
            'modified': modified,
            'generator': {
                'type': 'Application',
                'name': 'dit:directory',
            },
            'object': {
                'id': f'dit:directory:ExportPlan:{exportplan_id}',
                'type': 'dit:directory:ExportPlan',
                'dit:directory:ExportPlan:Section': 'about_your_business',
                'dit:directory:ExportPlan:Question': 'q_2',
                'dit:directory:ExportPlan:Response': 'response 2',
            },
        },
        {
            'id': f'dit:directory:ExportPlan:{exportplan_id}:Update',
            'modified': modified,
            'generator': {
                'type': 'Application',
                'name': 'dit:directory',
            },
            'object': {
                'id': f'dit:directory:ExportPlan:{exportplan_id}',
                'type': 'dit:directory:ExportPlan',
                'dit:directory:ExportPlan:Section': 'target_markets_research',
                'dit:directory:ExportPlan:Question': 'q_1',
                'dit:directory:ExportPlan:Response': 'response 3',
            },
        },
        {
            'id': f'dit:directory:ExportPlan:{exportplan_id}:Update',
            'modified': modified,
            'generator': {
                'type': 'Application',
                'name': 'dit:directory',
            },
            'object': {
                'id': f'dit:directory:ExportPlan:{exportplan_id}',
                'type': 'dit:directory:ExportPlan',
                'dit:directory:ExportPlan:Section': 'target_markets_research',
                'dit:directory:ExportPlan:Question': 'q_2',
                'dit:directory:ExportPlan:Response': 'response 4',
            },
        },
    ]


@pytest.mark.django_db
@mock.patch('activitystream.views.MAX_PER_PAGE', 1)
def test_activty_stream_company_viewset(api_client, companies_url):
    with freeze_time('2020-09-01 12:00:02'):
        company_1 = CompanyFactory(number='10000001', date_published=datetime.datetime(2020, 9, 1))
    with freeze_time('2012-09-01 12:00:01'):
        company_2 = CompanyFactory(number='10000002', date_published=datetime.datetime(2020, 9, 2))

    # Create a company without a date_published date. This shouldn't be included in the response
    CompanyFactory(number='10000003')

    # Page 1
    auth = _auth_sender(companies_url).request_header
    response = api_client.get(
        companies_url,
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json['orderedItems'] == [_expected_company_response(company_2)]

    # Page 2
    auth = _auth_sender(response_json['next']).request_header
    response = api_client.get(
        response_json['next'],
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json['orderedItems'] == [_expected_company_response(company_1)]

    # Page 3 (empty)
    auth = _auth_sender(response_json['next']).request_header
    response = api_client.get(
        response_json['next'],
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json['orderedItems'] == []
    assert 'next' not in response_json


@pytest.mark.django_db
@mock.patch('activitystream.views.MAX_PER_PAGE', 1)
def test_activty_stream_exportplan_viewset(api_client, exportplan_url):

    about_your_business = {"q_1": "response 1", "q_2": "response 2"}
    target_markets_research = {"q_1": "response 3", "q_2": "response 4"}

    with freeze_time('2020-09-01 12:00:02'):
        export_plan_1 = CompanyExportPlanFactory(
            about_your_business=about_your_business, target_markets_research=target_markets_research
        )

    with freeze_time('2020-11-01 12:00:02'):
        export_plan_2 = CompanyExportPlanFactory(
            about_your_business=about_your_business, target_markets_research=target_markets_research
        )

    # Page 1
    auth = _auth_sender(exportplan_url).request_header
    response = api_client.get(
        exportplan_url,
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json['orderedItems'] == _expected_export_plan_response(export_plan_1)

    # Page 2
    auth = _auth_sender(response_json['next']).request_header
    response = api_client.get(
        response_json['next'],
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )

    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json['orderedItems'] == _expected_export_plan_response(export_plan_2)

    # Page 3
    auth = _auth_sender(response_json['next']).request_header
    response = api_client.get(
        response_json['next'],
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json['orderedItems'] == []


@pytest.mark.django_db
@mock.patch('activitystream.views.MAX_PER_PAGE', 1)
def test_activty_stream_exportplan_viewset_empty_countries(api_client, exportplan_url):

    about_your_business = {"q_1": "response 1", "q_2": "response 2"}
    target_markets_research = {"q_1": "response 3", "q_2": "response 4"}

    with freeze_time('2020-09-01 12:00:02'):
        CompanyExportPlanFactory(
            about_your_business=about_your_business,
            target_markets_research=target_markets_research,
            export_countries=[],
        )

    # Page 1
    auth = _auth_sender(exportplan_url).request_header
    response = api_client.get(
        exportplan_url,
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    assert response.status_code == status.HTTP_200_OK
    response_json = response.json()
    assert response_json['orderedItems'][0]['object']['dit:directory:ExportPlan:Response'] == []
