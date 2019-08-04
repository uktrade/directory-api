import sigauth.middleware

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse


class SignatureCheckMiddleware(
    sigauth.middleware.SignatureCheckMiddlewareBase
):
    secret = settings.SIGNATURE_SECRET

    def should_check(self, request):
        if request.resolver_match.namespace in [
            'admin', 'healthcheck', 'authbroker_client'
        ] or request.path_info.startswith('/admin/login'):
            return False
        return super().should_check(request)


class AuthenticatedUserPermissionCheckMiddleware(MiddlewareMixin):

    def process_view(self, request, view_func, view_args, view_kwarg):
        if request.user.is_authenticated():
            if not request.user.is_staff:
                return HttpResponse('User not authorized for admin access', status=401)
