from rest_framework import permissions

from user.models import User as Supplier


class IsSSOAuthenticated(permissions.BasePermission):
    """
    Allows access only to authenticated sso users.
    """

    def has_permission(self, request, view):
        return isinstance(request.user, Supplier)
