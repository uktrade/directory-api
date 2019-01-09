import decimal

from elasticsearch_dsl.connections import connections
from health_check.backends import BaseHealthCheckBackend
from health_check.exceptions import (
    ServiceReturnedUnexpectedResult, ServiceUnavailable
)


class ElasticSearchCheckBackend(BaseHealthCheckBackend):

    def check_status(self):
        connection = connections.get_connection()
        if not connection.ping():
            raise ServiceUnavailable('Elasticsearch ping error')
        return True


class StannpBackend(BaseHealthCheckBackend):
    def check_status(self):
        from company.stannp import stannp_client

        try:
            response = stannp_client.retrieve_balance()
        except Exception as error:
            raise ServiceUnavailable('(Stannp) ' + str(error))
        else:
            if response.status_code != 200:
                raise ServiceReturnedUnexpectedResult(
                    f'Stannp returned {response.status_code} status code'
                )
            else:
                balance = decimal.Decimal(response.json()['data']['balance'])
                if balance < 50:
                    raise ServiceReturnedUnexpectedResult(
                        f'Balance is {balance}. Top up soon.'
                    )
        return True
