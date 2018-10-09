from unittest.mock import Mock, patch

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


@patch('supplier.helpers.sso_api_client.ping',
       Mock(side_effect=Exception('oops')))
def test_single_sign_on_ping_connection_error():
    backend = backends.SigngleSignOnBackend()
    backend.run_check()

    assert backend.pretty_status() == 'unavailable: (sso proxy) oops'


@patch('supplier.helpers.sso_api_client.ping',
       Mock(return_value=Mock(status_code=500)))
def test_single_sign_on_ping_not_ok():
    backend = backends.SigngleSignOnBackend()
    backend.run_check()

    assert backend.pretty_status() == (
        'unexpected result: sso proxy returned 500 status code'
    )


@patch('supplier.helpers.sso_api_client.ping',
       Mock(return_value=Mock(status_code=200)))
def test_single_sign_on_ping_ok():
    backend = backends.SigngleSignOnBackend()
    backend.run_check()

    assert backend.pretty_status() == 'working'


@patch('healthcheck.backends.stannp_client.retrieve_balance',
       Mock(side_effect=Exception('oops')))
def test_stannp_balance_connection_error():
    backend = backends.StannpBackend()
    backend.run_check()

    assert backend.pretty_status() == 'unavailable: (Stannp) oops'


@patch('healthcheck.backends.stannp_client.retrieve_balance',
       Mock(return_value=Mock(status_code=500)))
def test_stannp_balance_not_ok():
    backend = backends.StannpBackend()
    backend.run_check()

    assert backend.pretty_status() == (
        'unexpected result: Stannp returned 500 status code'
    )


@patch('healthcheck.backends.stannp_client.retrieve_balance')
def test_stannp_balance_ok(mock_retrieve_balance):
    mock_retrieve_balance.return_value = Mock(
        status_code=200,
        json=lambda: {
            'data': {
                'balance': '100.02'
            }
        }
    )
    backend = backends.StannpBackend()
    backend.run_check()

    assert backend.pretty_status() == 'working'


@patch('healthcheck.backends.stannp_client.retrieve_balance')
def test_stannp_balance_too_low(mock_retrieve_balance):
    mock_retrieve_balance.return_value = Mock(
        status_code=200,
        json=lambda: {
            'data': {
                'balance': '49.99'
            }
        }
    )
    backend = backends.StannpBackend()
    backend.run_check()

    assert backend.pretty_status() == (
        'unexpected result: Balance is 49.99. Top up soon.'
    )
