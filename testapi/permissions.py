from django.conf import settings
from django.utils.crypto import constant_time_compare
from rest_framework import permissions


class IsAuthenticatedTestAPI(permissions.BasePermission):
    """Allow token access to test API."""

    def has_permission(self, request, view):
        return constant_time_compare(
            request.GET.get('token'),
            settings.TEST_API_AUTH_TOKEN
        )
