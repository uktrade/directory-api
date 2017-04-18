from sigauth import permissions

from django.conf import settings


class SignatureCheckPermission(permissions.SignatureCheckPermissionBase):
    secret = settings.API_CLIENT_KEY
