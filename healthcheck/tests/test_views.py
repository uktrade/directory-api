from unittest.mock import patch

from rest_framework import status

from django.core.urlresolvers import reverse


@patch(
    'healthcheck.backends.StannpBackend.check_status', return_value=True
)
def test_healthcheck_stannp(mock_check_status, client, settings):
    response = client.get(
        reverse('healthcheck:stannp'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_check_status.call_count == 1


@patch(
    'healthcheck.backends.SigngleSignOnBackend.check_status',
    return_value=True
)
def test_healthcheck_single_sign_on(mock_check_status, client, settings):
    response = client.get(
        reverse('healthcheck:single-sign-on'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_check_status.call_count == 1


@patch(
    'health_check.db.backends.DatabaseBackend.check_status', return_value=True
)
def test_healthcheck_database(mock_check_status, client, settings):
    response = client.get(
        reverse('healthcheck:database'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_check_status.call_count == 1


@patch(
    'health_check.cache.backends.CacheBackend.check_status', return_value=True
)
def test_healthcheck_cache(mock_check_status, client, settings):
    response = client.get(
        reverse('healthcheck:cache'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_check_status.call_count == 1


@patch(
    'healthcheck.backends.ElasticSearchCheckBackend.check_status',
    return_value=True
)
def test_healthcheck_elasticsearch(mock_check_status, client, settings):
    response = client.get(
        reverse('healthcheck:elastic-search'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_check_status.call_count == 1
