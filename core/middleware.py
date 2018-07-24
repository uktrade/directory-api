import logging

from admin_ip_restrictor import middleware

from django.http import Http404

from core import helpers


logger = logging.getLogger(__name__)


class AdminIPRestrictorMiddleware(middleware.AdminIPRestrictorMiddleware):
    MESSAGE_UNABLE_TO_DETERMINE_IP_ADDRESS = 'Unable to determine remote IP'

    def get_ip(self, request):
        return helpers.RemoteIPAddressRetriver().get_ip_address(request)

    def process_request(self, request):
        try:
            return super().process_request(request)
        except LookupError:
            logger.exception(self.MESSAGE_UNABLE_TO_DETERMINE_IP_ADDRESS)
            raise Http404()
