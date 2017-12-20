from elasticsearch_dsl.connections import connections
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import (
    ServiceReturnedUnexpectedResult, ServiceUnavailable
)

from supplier.helpers import sso_api_client


class ElasticSearchCheckBackend(BaseHealthCheckBackend):

    def check_status(self):
        connection = connections.get_connection()
        if not connection.ping():
            raise ServiceUnavailable('Elasticsearch ping error')
        return True


class SigngleSignOnBackend(BaseHealthCheckBackend):

    message_bad_status = 'sso proxy returned {0.status_code} status code'

    def check_status(self):
        try:
            response = sso_api_client.ping()
        except Exception as error:
            raise ServiceUnavailable('(sso proxy) ' + str(error))
        else:
            if response.status_code != 200:
                raise ServiceReturnedUnexpectedResult(
                    self.message_bad_status.format(response)
                )
        return True
