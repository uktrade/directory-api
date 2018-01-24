from django.conf import settings
from django.utils.crypto import constant_time_compare
from rest_framework import permissions

from supplier.helpers import SSOUser


class IsAuthenticatedSSO(permissions.BasePermission):
    """
    Allows access only to authenticated sso users.
    """

    def has_permission(self, request, view):
        return isinstance(request.user, SSOUser)


class IsAuthenticatedCSVDump(permissions.BasePermission):
    """Allow token access to data science team."""

    def has_permission(self, request, view):
        return constant_time_compare(
            request.GET.get('token'),
            settings.CSV_DUMP_AUTH_TOKEN
        )
