from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import ServiceUnavailable
from opensearch_dsl.connections import connections


class ElasticSearchCheckBackend(BaseHealthCheckBackend):
    def check_status(self):
        connection = connections.get_connection()
        if not connection.ping():
            raise ServiceUnavailable('Elasticsearch ping error')
        return True
