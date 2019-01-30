import datetime

import mohawk
import pytest
from freezegun import freeze_time
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from company.tests.factories import CompanyFactory


@pytest.fixture
def api_client():
    return APIClient()


def _url():
    return 'http://testserver' + reverse('activity-stream:activity-stream')


def _url_incorrect_domain():
    return 'http://incorrect' + reverse('activity-stream:activity-stream')


def _url_incorrect_path():
    return (
        'http://testserver' +
        reverse('activity-stream:activity-stream') +
        'incorrect/'
    )


def _empty_collection():
    return {
        '@context': [
            'https://www.w3.org/ns/activitystreams', {
                'dit': 'https://www.trade.gov.uk/ns/activitystreams/v1',
            }
        ],
        'type': 'Collection',
        'orderedItems': [],
    }


def _auth_sender(key_id='some-id', secret_key='some-secret', url=_url,
                 method='GET', content='', content_type=''):
    credentials = {
        'id': key_id,
        'key': secret_key,
        'algorithm': 'sha256',
    }
    return mohawk.Sender(
        credentials,
        url(),
        method,
        content=content,
        content_type=content_type,
    )


def get_companies_house_number(activity):
    """Returns the companies house number of an activity"""
    return activity['object']['dit:companiesHouseNumber']


@pytest.mark.django_db
def test_empty_object_returned_with_authentication(api_client):
    """If the Authorization and X-Forwarded-For headers are correct, then
    the correct, and authentic, data is returned
    """
    sender = _auth_sender()
    response = api_client.get(
        _url(),
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
def test_if_never_verified_not_in_stream(api_client):
    """If the company never verified, then it's not in the activity stream
    """

    with freeze_time('2012-01-14 12:00:02'):
        CompanyFactory()

    sender = _auth_sender()
    response = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        '@context': [
            'https://www.w3.org/ns/activitystreams', {
                'dit': 'https://www.trade.gov.uk/ns/activitystreams/v1',
            }
        ],
        'type': 'Collection',
        'orderedItems': [],
        'next': 'http://testserver/activity-stream/?after=1326542402.0_3',
    }


@pytest.mark.django_db
def test_if_verified_with_code_in_stream_in_date_then_seq_order(api_client):
    """If the company verified_with_code, then it's in the activity stream
    """

    CompanyFactory(number=10000000)

    with freeze_time('2012-01-14 12:00:02'):
        CompanyFactory(number=10000003, verified_with_code=True)

    with freeze_time('2012-01-14 12:00:02'):
        CompanyFactory(number=10000002, verified_with_code=True)

    with freeze_time('2012-01-14 12:00:01'):
        CompanyFactory(number=10000001, verified_with_code=True)

    sender = _auth_sender()
    response = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    items = response.json()['orderedItems']

    assert len(items) == 3
    assert items[0]['published'] == '2012-01-14T12:00:01+00:00'
    assert get_companies_house_number(items[0]) == '10000001'
    assert items[1]['published'] == '2012-01-14T12:00:02+00:00'
    assert get_companies_house_number(items[1]) == '10000003'
    assert items[2]['published'] == '2012-01-14T12:00:02+00:00'
    assert get_companies_house_number(items[2]) == '10000002'


@pytest.mark.django_db
def test_if_verified_with_code_then_deleted_not_in_stream(api_client):
    """If the company verified_with_code, then deleted, then not in the stream

    This may need to be changed, but this confirms/documents behaviour, and
    ensures that the endpoint doesn't break in this case
    """

    to_delete = CompanyFactory(number=10000001, verified_with_code=True)
    CompanyFactory(number=10000002, verified_with_code=True)

    to_delete.delete()

    sender = _auth_sender()
    response = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    items = response.json()['orderedItems']

    assert len(items) == 1
    assert get_companies_house_number(items[0]) == '10000002'


@pytest.mark.django_db
def test_if_verified_with_companies_house_oauth2_in_stream(api_client):
    """If the company verified_with_companies_house_oauth2, then it's n the
    activity stream
    """

    CompanyFactory(number=10000000, verified_with_companies_house_oauth2=True)

    sender = _auth_sender()
    response = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    items = response.json()['orderedItems']

    assert len(items) == 1
    assert get_companies_house_number(items[0]) == '10000000'


@pytest.mark.django_db
def test_if_verified_with_preverified_enrolment_in_stream(api_client):
    """If the company verified_with_preverified_enrolment, then it's in the
    activity stream
    """

    CompanyFactory(number=10000000, verified_with_preverified_enrolment=True)

    sender = _auth_sender()
    response = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    items = response.json()['orderedItems']

    assert len(items) == 1
    assert get_companies_house_number(items[0]) == '10000000'


@pytest.mark.django_db
def test_pagination(api_client, django_assert_num_queries):
    """The requests are paginated, ending on a page without a next key
    """

    with freeze_time('2012-01-14 12:00:02'):
        for i in range(0, 250):
            CompanyFactory(number=10000000 + i,
                           verified_with_preverified_enrolment=True)

    with freeze_time('2012-01-14 12:00:01'):
        for i in range(250, 501):
            CompanyFactory(number=10000000 + i,
                           verified_with_preverified_enrolment=True)

    items = []
    next_url = _url()
    num_pages = 0

    with django_assert_num_queries(9):
        while next_url:
            num_pages += 1
            sender = _auth_sender(url=lambda: next_url)
            response = api_client.get(
                next_url,
                content_type='',
                HTTP_AUTHORIZATION=sender.request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
            )
            response_json = response.json()
            items += response_json['orderedItems']
            next_url = \
                response_json['next'] if 'next' in response_json else \
                None

    assert num_pages == 5
    assert len(items) == 501
    assert len(set([item['id'] for item in items])) == 501
    assert get_companies_house_number(items[500]) == '10000249'


@pytest.mark.django_db
def test_if_61_seconds_in_past_401_returned(api_client):
    """If the Authorization header is generated 61 seconds in the past, then a
    401 is returned
    """
    past = datetime.datetime.now() - datetime.timedelta(seconds=61)
    with freeze_time(past):
        auth = _auth_sender().request_header
    response = api_client.get(
        reverse('activity-stream:activity-stream'),
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error = {'detail': 'Incorrect authentication credentials.'}
    assert response.json() == error
