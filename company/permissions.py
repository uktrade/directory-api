from directory_constants import user_roles
from rest_framework import permissions


class IsCompanyAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.company_user.role == user_roles.ADMIN
