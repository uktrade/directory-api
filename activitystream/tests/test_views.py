import datetime

from freezegun import freeze_time
import mohawk


def auth_header(key_id, secret_key, url, method, content, content_type):
    return mohawk.Sender({
        'id': key_id,
        'key': secret_key,
        'algorithm': 'sha256',
    },
        url,
        method,
        content=content,
        content_type=content_type,
    ).request_header


def test_if_authentication_not_passed_then_401_returned(client):
    response = client.get(
        '/activity-stream/',
    )

    assert response.status_code == 401
    error = b'{"detail":"Authentication credentials were not provided."}'
    assert response.content == error


def test_if_authentication_passed_but_61_seconds_in_past_401_returned(client):
    past = datetime.datetime.now() + datetime.timedelta(seconds=-61)
    with freeze_time(past):
        auth = auth_header(
            'some-id', 'some-secret',
            'http://testserver/activity-stream/', 'GET', '', ''
        )
    response = client.get(
        '/activity-stream/',
        HTTP_AUTHORIZATION=auth,
    )

    assert response.status_code == 401
    error = b'{"detail":"Incorrect authentication credentials."}'
    assert response.content == error


def test_if_authentication_reused_401_returned(client):
    auth = auth_header(
        'some-id', 'some-secret',
        'http://testserver/activity-stream/', 'GET', '', ''
    )
    response_1 = client.get(
        '/activity-stream/',
        HTTP_AUTHORIZATION=auth,
    )
    assert response_1.status_code == 200

    response_2 = client.get(
        '/activity-stream/',
        HTTP_AUTHORIZATION=auth,
    )
    assert response_2.status_code == 401
    error = b'{"detail":"Incorrect authentication credentials."}'
    assert response_2.content == error


def test_if_incorrect_id_then_401_returned(client):
    auth = auth_header(
        'some-id-incorrect', 'some-secret',
        'http://testserver/activity-stream/', 'GET', '', ''
    )
    response = client.get(
        '/activity-stream/',
        HTTP_AUTHORIZATION=auth,
    )

    assert response.status_code == 401
    error = b'{"detail":"Incorrect authentication credentials."}'
    assert response.content == error


def test_if_incorrect_secret_then_401_returned(client):
    auth = auth_header(
        'some-id', 'some-secret-incorrect',
        'http://testserver/activity-stream/', 'GET', '', ''
    )
    response = client.get(
        '/activity-stream/',
        HTTP_AUTHORIZATION=auth,
    )

    assert response.status_code == 401
    error = b'{"detail":"Incorrect authentication credentials."}'
    assert response.content == error


def test_if_incorrect_domain_then_401_returned(client):
    auth = auth_header(
        'some-id', 'some-secret',
        'http://incorrect/activity-stream/', 'GET', '', ''
    )
    response = client.get(
        '/activity-stream/',
        HTTP_AUTHORIZATION=auth,
    )

    assert response.status_code == 401
    error = b'{"detail":"Incorrect authentication credentials."}'
    assert response.content == error


def test_if_incorrect_path_then_401_returned(client):
    auth = auth_header(
        'some-id', 'some-secret',
        'http://testserver/incorrect/', 'GET', '', ''
    )
    response = client.get(
        '/activity-stream/',
        HTTP_AUTHORIZATION=auth,
    )

    assert response.status_code == 401
    error = b'{"detail":"Incorrect authentication credentials."}'
    assert response.content == error


def test_if_incorrect_method_then_401_returned(client):
    auth = auth_header(
        'some-id', 'some-secret',
        'http://testserver/activity-stream/', 'POST', '', ''
    )
    response = client.get(
        '/activity-stream/',
        HTTP_AUTHORIZATION=auth,
    )

    assert response.status_code == 401
    error = b'{"detail":"Incorrect authentication credentials."}'
    assert response.content == error


def test_if_incorrect_content_type_then_401_returned(client):
    auth = auth_header(
        'some-id', 'some-secret',
        'http://testserver/activity-stream/', 'GET', 'incorrect', ''
    )
    response = client.get(
        '/activity-stream/',
        HTTP_AUTHORIZATION=auth,
    )

    assert response.status_code == 401
    error = b'{"detail":"Incorrect authentication credentials."}'
    assert response.content == error


def test_if_incorrect_content_then_401_returned(client):
    auth = auth_header(
        'some-id', 'some-secret',
        'http://testserver/activity-stream/', 'GET', '', 'incorrect'
    )
    response = client.get(
        '/activity-stream/',
        HTTP_AUTHORIZATION=auth,
    )

    assert response.status_code == 401
    error = b'{"detail":"Incorrect authentication credentials."}'
    assert response.content == error


def test_empty_object_returned(client):
    auth = auth_header(
        'some-id', 'some-secret',
        'http://testserver/activity-stream/', 'GET', '', ''
    )
    response = client.get(
        '/activity-stream/',
        HTTP_AUTHORIZATION=auth,
    )

    assert response.status_code == 200
    assert response.content == b'{"secret":"content-for-pen-test"}'
