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
    return 'http://testserver' + reverse('activity-stream')


def _url_incorrect_domain():
    return 'http://incorrect' + reverse('activity-stream')


def _url_incorrect_path():
    return 'http://testserver' + reverse('activity-stream') + 'incorrect/'


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


@pytest.mark.parametrize(
    'get_kwargs,expected_json',
    (
        (
            # If no X-Forwarded-For header
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If second-to-last X-Forwarded-For header isn't whitelisted
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
                HTTP_X_FORWARDED_FOR='9.9.9.9, 123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the only IP address in X-Forwarded-For is whitelisted
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the only IP address in X-Forwarded-For isn't whitelisted
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
                HTTP_X_FORWARDED_FOR='123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If third-to-last IP in X-Forwarded-For header is whitelisted
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4, 124.124.124, 123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If last of 3 IPs in X-Forwarded-For header is whitelisted
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender().request_header,
                HTTP_X_FORWARDED_FOR='124.124.124, 123.123.123.123, 1.2.3.4',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header isn't passed
            dict(
                content_type='',
                HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
            ),
            {'detail': 'Authentication credentials were not provided.'},
        ),
        (
            # If the Authorization header generated from an incorrect ID
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    key_id='incorrect',
                ).request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect secret
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    secret_key='incorrect'
                ).request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect domain
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    url=_url_incorrect_domain,
                ).request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect path
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    url=_url_incorrect_path,
                ).request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect method
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    method='POST',
                ).request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from an incorrect
            # content-type
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    content_type='incorrect',
                ).request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
        (
            # If the Authorization header generated from incorrect content
            dict(
                content_type='',
                HTTP_AUTHORIZATION=_auth_sender(
                    content='incorrect',
                ).request_header,
                HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
            ),
            {'detail': 'Incorrect authentication credentials.'},
        ),
    ),
)
@pytest.mark.django_db
def test_401_returned(api_client, get_kwargs, expected_json):
    """If the request isn't properly Hawk-authenticated, then a 401 is
    returned
    """
    response = api_client.get(
        _url(),
        **get_kwargs,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == expected_json


@pytest.mark.django_db
def test_if_61_seconds_in_past_401_returned(api_client):
    """If the Authorization header is generated 61 seconds in the past, then a
    401 is returned
    """
    past = datetime.datetime.now() - datetime.timedelta(seconds=61)
    with freeze_time(past):
        auth = _auth_sender().request_header
    response = api_client.get(
        reverse('activity-stream'),
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    error = {'detail': 'Incorrect authentication credentials.'}
    assert response.json() == error


@pytest.mark.django_db
def test_if_authentication_reused_401_returned(api_client):
    """If the Authorization header is reused, then a 401 is returned"""
    auth = _auth_sender().request_header

    response_1 = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    assert response_1.status_code == status.HTTP_200_OK

    response_2 = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=auth,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    assert response_2.status_code == status.HTTP_401_UNAUTHORIZED
    error = {'detail': 'Incorrect authentication credentials.'}
    assert response_2.json() == error


@pytest.mark.django_db
def test_empty_object_returned_with_authentication_3_ips(api_client):
    """If the Authorization and X-Forwarded-For headers are correct,
    with an extra IP address prepended to the X-Forwarded-For then
    the correct, and authentic, data is returned
    """
    sender = _auth_sender()
    response = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='3.3.3.3, 1.2.3.4, 123.123.123.123',
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == _empty_collection()


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
    CompanyFactory()

    sender = _auth_sender()
    response = api_client.get(
        _url(),
        content_type='',
        HTTP_AUTHORIZATION=sender.request_header,
        HTTP_X_FORWARDED_FOR='1.2.3.4, 123.123.123.123',
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == _empty_collection()


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
    assert items[0]['object']['dit:companiesHouseNumber'] == '10000001'
    assert items[1]['published'] == '2012-01-14T12:00:02+00:00'
    assert items[1]['object']['dit:companiesHouseNumber'] == '10000003'
    assert items[2]['published'] == '2012-01-14T12:00:02+00:00'
    assert items[2]['object']['dit:companiesHouseNumber'] == '10000002'


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
    assert items[0]['object']['dit:companiesHouseNumber'] == '10000000'


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
    assert items[0]['object']['dit:companiesHouseNumber'] == '10000000'
