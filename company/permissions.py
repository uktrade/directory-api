from rest_framework import permissions


class IsCaseStudyOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.META.get('sso-id'):
            return False
        return obj.company.suppliers.filter(sso_id=request.META['sso-id'])
