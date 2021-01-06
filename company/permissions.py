from directory_constants import user_roles
from django.conf import settings
from rest_framework import permissions


class IsCompanyAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.company_user.role == user_roles.ADMIN


class ValidateDeleteRequest(permissions.BasePermission):
    """Allow token access to data science team."""

    def has_permission(self, request, view):
        return request.parser_context['kwargs']['request_key'] == settings.DIRECTORY_SSO_API_SECRET
