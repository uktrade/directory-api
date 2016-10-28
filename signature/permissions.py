from rest_framework import permissions

from signature.utils import SignatureRejection


class SignaturePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return SignatureRejection.test_signature(request)
