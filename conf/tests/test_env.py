import json
import os
from importlib import reload
from unittest import mock

import environ
import pytest
from opensearchpy import RequestsHttpConnection

# from config.env import DBTPlatformEnvironment, GovPaasEnvironment, env
from conf import env as environment_reader


@pytest.fixture
def environment():
    env = environ.Env()
    for env_file in env.list('ENV_FILES', default=[]):
        env.read_env(f'conf/env/{env_file}')


@pytest.fixture
def vcap_services():
    data = {
        'postgres': [
            {
                'binding_guid': '123',
                'binding_name': None,
                'credentials': {
                    'host': 'example.com',
                    'jdbcuri': 'jdbc:postgresql://example.com:5432/exampledb',
                    'name': 'exampledb',
                    'password': 'examplepassword',
                    'port': 5432,
                    'uri': 'postgres://exampleuser:examplepassword@example.com:5432/exampledb',
                    'username': 'exampleuser',
                },
                'instance_guid': '1234',
                'instance_name': 'great-cms-db',
                'label': 'postgres',
                'name': 'great-cms-db',
                'plan': 'medium-ha',
                'provider': None,
                'syslog_drain_url': None,
                'tags': ['postgres', 'relational'],
                'volume_mounts': [],
            }
        ],
        'redis': [
            {
                'binding_guid': '456',
                'binding_name': None,
                'credentials': {
                    'host': 'example.com',
                    'name': 'exampleuser',
                    'password': 'examplepassword',
                    'port': 6379,
                    'tls_enabled': True,
                    'uri': 'rediss://examplepassword@example.com:6379',
                },
                'instance_guid': '4567',
                'instance_name': 'great-cms-redis-small',
                'label': 'redis',
                'name': 'great-cms-redis-small-ha-6',
                'plan': 'small-ha',
                'provider': None,
                'syslog_drain_url': None,
                'tags': ['elasticache', 'redis'],
                'volume_mounts': [],
            }
        ],
        'opensearch': [
            {
                'binding_guid': '789',
                'binding_name': None,
                'credentials': {
                    'hostname': 'example.com',
                    'password': 'examplepassword',
                    'port': 19676,
                    'uri': 'https://exampleuser:examplepassword@example.com:19676',
                    'username': 'exampleuser',
                },
                'instance_guid': '7890',
                'instance_name': 'directory-api-opensearch',
                'label': 'opensearch',
                'name': 'directory-api-opensearch',
                'plan': 'medium-ha-1',
                'provider': None,
                'syslog_drain_url': None,
                'tags': [],
                'volume_mounts': [],
            }
        ],
    }
    return json.dumps(data)


@pytest.fixture
def vcap_application():
    data = {
        'application_id': '12345',
        'application_name': 'great-cms',
        'application_uris': ['www.example.com'],
        'cf_api': 'https://api.example.com',
        'limits': {'fds': 1},
        'name': 'great-cms',
        'organization_id': '67890',
        'organization_name': 'example-org',
        'space_id': '98765',
        'space_name': 'example-space',
        'uris': ['www.example.com'],
        'users': None,
    }
    return json.dumps(data)


@pytest.fixture
def database_credentials():
    data = {
        'engine': 'postgres',
        'username': 'exampleuser',
        'password': 'examplepassword',
        'dbname': 'exampledb',
        'host': 'example.com',
        'port': 5432,
    }
    return json.dumps(data)


def test_gov_paas_environment(vcap_application, vcap_services, environment):
    os.environ.pop('CIRCLECI', None)
    os.environ['APP_ENVIRONMENT'] = 'local'
    os.environ['VCAP_SERVICES'] = vcap_services
    os.environ['VCAP_APPLICATION'] = vcap_application

    reload(environment_reader)

    os.environ['CIRCLECI'] = 'true'

    assert isinstance(environment_reader.env, environment_reader.GovPaasEnvironment)
    assert environment_reader.env.app_environment == 'local'
    assert environment_reader.env.secret_key == 'debug'
    assert environment_reader.env.database_url == 'postgres://exampleuser:examplepassword@example.com:5432/exampledb'
    assert environment_reader.env.redis_url == 'rediss://examplepassword@example.com:6379'
    assert environment_reader.env.vcap_application.name == 'great-cms'
    assert environment_reader.env.allowed_hosts_list == ['*']
    assert environment_reader.env.opensearch_url == 'https://exampleuser:examplepassword@example.com:19676'
    assert environment_reader.env.opensearch_config == {
        'alias': 'default',
        'connection_class': RequestsHttpConnection,
        'hosts': ['https://exampleuser:examplepassword@example.com:19676'],
        'http_compress': True,
    }

    environment_reader.env.vcap_services = None

    assert environment_reader.env.database_url == 'postgres://'
    assert environment_reader.env.redis_url == 'rediss://'
    assert environment_reader.env.opensearch_url == 'https://'


@mock.patch('dbt_copilot_python.network.setup_allowed_hosts', mock.Mock(return_value=['*']))
def test_dbt_platform_environment(database_credentials, environment):
    os.environ.pop('CIRCLECI', None)
    os.environ['APP_ENVIRONMENT'] = 'local'
    os.environ['COPILOT_ENVIRONMENT_NAME'] = 'test'
    os.environ['DATABASE_CREDENTIALS'] = database_credentials
    os.environ['CELERY_BROKER_URL'] = 'rediss://examplepassword@example.com:6379'
    os.environ['OPENSEARCH_URL'] = 'https://exampleuser:examplepassword@example.com:19676'

    reload(environment_reader)

    os.environ['CIRCLECI'] = 'true'

    assert isinstance(environment_reader.env, environment_reader.DBTPlatformEnvironment)
    assert environment_reader.env.app_environment == 'local'
    assert environment_reader.env.secret_key == 'debug'
    assert environment_reader.env.database_url == 'postgres://exampleuser:examplepassword@example.com:5432/exampledb'
    assert environment_reader.env.redis_url == 'rediss://examplepassword@example.com:6379'
    assert environment_reader.env.opensearch_url == 'https://exampleuser:examplepassword@example.com:19676'
    assert environment_reader.env.allowed_hosts_list == ['*']
    assert environment_reader.env.opensearch_config == {
        'alias': 'default',
        'connection_class': RequestsHttpConnection,
        'hosts': ['https://exampleuser:examplepassword@example.com:19676'],
        'http_compress': True,
    }


def test_ci_environment():
    os.environ['DATABASE_URL'] = 'postgres://exampleuser:examplepassword@example.com:5432/exampledb'
    os.environ['REDIS_URL'] = 'rediss://examplepassword@example.com:6379'
    os.environ['OPENSEARCH_URL'] = 'https://exampleuser:examplepassword@example.com:19676'

    reload(environment_reader)

    assert isinstance(environment_reader.env, environment_reader.CIEnvironment)
    assert environment_reader.env.app_environment == 'local'
    assert environment_reader.env.secret_key == 'debug'
    assert environment_reader.env.database_url == 'postgres://exampleuser:examplepassword@example.com:5432/exampledb'
    assert environment_reader.env.redis_url == 'rediss://examplepassword@example.com:6379'


def test_local_docker_ci_environment():
    os.environ['IS_DOCKER'] = 'true'

    reload(environment_reader)

    assert isinstance(environment_reader.env, environment_reader.CIEnvironment)
    assert environment_reader.env.opensearch_config['hosts'] == ['docker-opensearch:9200']
