from rest_framework import permissions


class IsCompanyProfileOwner(permissions.BasePermission):
    """
    Allows access only to company profile owners.
    """

    def has_permission(self, request, view):
        return request.user.supplier.is_company_owner
