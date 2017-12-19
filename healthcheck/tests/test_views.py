from unittest.mock import patch

from rest_framework import status

from django.core.urlresolvers import reverse


def test_ping(client):
    response = client.get(reverse('health-check-ping'))

    assert response.status_code == status.HTTP_200_OK


@patch(
    'health_check.db.backends.DatabaseBackend.check_status', return_value=True
)
def test_database(mock_check_status, client, settings):
    response = client.get(
        reverse('health-check-database'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_check_status.call_count == 1


@patch(
    'health_check.cache.backends.CacheBackend.check_status', return_value=True
)
def test_cache(mock_check_status, client, settings):
    response = client.get(
        reverse('health-check-cache'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_check_status.call_count == 1


@patch(
    'healthcheck.backends.SigngleSignOnBackend.check_status', return_value=True
)
def test_single_sign_on(mock_check_status, client, settings):
    response = client.get(
        reverse('health-check-single-sign-on'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_check_status.call_count == 1


@patch(
    'healthcheck.backends.ElasticSearchCheckBackend.check_status',
    return_value=True
)
def test_elasticsearch(mock_check_status, client, settings):
    response = client.get(
        reverse('health-check-elastic-search'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_check_status.call_count == 1
