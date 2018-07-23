from admin_ip_restrictor import middleware

from core import helpers


class AdminIPRestrictorMiddleware(middleware.AdminIPRestrictorMiddleware):
    def get_ip(self, request):
        return helpers.RemoteIPAddress().get_ip_address(request)
