from directory_healthcheck.views import BaseHealthCheckAPIView
from health_check.db.backends import DatabaseBackend
from health_check.cache.backends import CacheBackend

from healthcheck.backends import (
    ElasticSearchCheckBackend, StannpBackend, SigngleSignOnBackend
)


class DatabaseAPIView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return DatabaseBackend()


class CacheAPIView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return CacheBackend()


class ElasticsearchAPIView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return ElasticSearchCheckBackend()


class StannpView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return StannpBackend()


class SingleSignOnHealthcheckView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return SigngleSignOnBackend()
