from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from directory_healthcheck.views import BaseHealthCheckAPIView
from health_check.db.backends import DatabaseBackend
from health_check.cache.backends import CacheBackend

from healthcheck.backends import (
    ElasticSearchCheckBackend, SigngleSignOnBackend
)


class DatabaseAPIView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return DatabaseBackend()


class CacheAPIView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return CacheBackend()


class SingleSignOnAPIView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return SigngleSignOnBackend()


class ElasticsearchAPIView(BaseHealthCheckAPIView):
    def create_service_checker(self):
        return ElasticSearchCheckBackend()


class PingAPIView(APIView):

    permission_classes = []
    http_method_names = ("get", )

    def get(self, request, *args, **kwargs):
        return Response(status=status.HTTP_200_OK)
