from unittest.mock import patch

from rest_framework import status

from django.core.urlresolvers import reverse


@patch(
    'health_check.db.backends.DatabaseBackend.check_status', return_value=True
)
def test_database(mock_check_status, client, settings):
    response = client.get(
        reverse('healthcheck:database'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_check_status.call_count == 1


@patch(
    'health_check.cache.backends.CacheBackend.check_status', return_value=True
)
def test_cache(mock_check_status, client, settings):
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
def test_elasticsearch(mock_check_status, client, settings):
    response = client.get(
        reverse('healthcheck:elastic-search'),
        {'token': settings.HEALTH_CHECK_TOKEN},
    )

    assert response.status_code == status.HTTP_200_OK
    assert mock_check_status.call_count == 1
