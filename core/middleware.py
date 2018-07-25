import admin_ip_restrictor.middleware
import sigauth.middleware

from django.conf import settings
from django.http import Http404

import logging


from core import helpers


logger = logging.getLogger(__name__)


class AdminIPRestrictorMiddleware(
    admin_ip_restrictor.middleware.AdminIPRestrictorMiddleware
):
    MESSAGE_UNABLE_TO_DETERMINE_IP_ADDRESS = 'Unable to determine remote IP'

    def get_ip(self, request):
        try:
            return helpers.RemoteIPAddressRetriver().get_ip_address(request)
        except LookupError:
            logger.exception(self.MESSAGE_UNABLE_TO_DETERMINE_IP_ADDRESS)
            raise Http404()


class SignatureCheckMiddleware(
    sigauth.middleware.SignatureCheckMiddlewareBase
):
    secret = settings.SIGNATURE_SECRET

    def should_check(self, request):
        if request.resolver_match.namespace == 'admin':
            return False
        return super().should_check(request)
