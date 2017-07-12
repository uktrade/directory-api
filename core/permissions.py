from rest_framework import permissions

from supplier.helpers import SSOUser


class IsAuthenticatedSSO(permissions.BasePermission):
    """
    Allows access only to authenticated sso users.
    """

    def has_permission(self, request, view):
        return isinstance(request.user, SSOUser)
