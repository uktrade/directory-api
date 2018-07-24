import admin_ip_restrictor.middleware
import sigauth.middleware

from django.conf import settings

from core import helpers


class AdminIPRestrictorMiddleware(
    admin_ip_restrictor.middleware.AdminIPRestrictorMiddleware
):
    def get_ip(self, request):
        return helpers.RemoteIPAddressRetriver().get_ip_address(request)


class SignatureCheckMiddleware(
    sigauth.middleware.SignatureCheckMiddlewareBase
):
    secret = settings.SIGNATURE_SECRET

    def should_check(self, request):
        if request.resolver_match.namespace == 'admin':
            return False
        return super().should_check(request)
