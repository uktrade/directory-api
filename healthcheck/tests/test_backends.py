from unittest.mock import patch

from healthcheck import backends


@patch('elasticsearch_dsl.connections.connections.get_connection')
def test_elasticsearch_ping_error(mock_get_connection):
    mock_get_connection.return_value.ping.return_value = False
    backend = backends.ElasticSearchCheckBackend()
    backend.run_check()

    assert backend.pretty_status() == 'unavailable: Elasticsearch ping error'


@patch('elasticsearch_dsl.connections.connections.get_connection')
def test_elasticsearch_ping_ok(mock_get_connection):
    mock_get_connection.return_value.ping.return_value = True
    backend = backends.ElasticSearchCheckBackend()
    backend.run_check()

    assert backend.pretty_status() == 'working'
