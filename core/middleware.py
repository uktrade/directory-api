import sigauth.middleware
from django.conf import settings
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin


class SignatureCheckMiddleware(sigauth.middleware.SignatureCheckMiddlewareBase):
    secret = settings.SIGNATURE_SECRET

    def should_check(self, request):
        if (
            request.resolver_match.namespace in ['admin', 'healthcheck', 'authbroker_client']
        ) or request.path_info.startswith('/admin/login'):
            return False
        return super().should_check(request)


class AdminPermissionCheckMiddleware(MiddlewareMixin):
    SSO_UNAUTHORISED_ACCESS_MESSAGE = (
        'This application now uses internal Single Sign On. Please email '
        'directory@digital.trade.gov.uk so that we can enable your account.'
    )

    def process_view(self, request, view_func, view_args, view_kwarg):
        if request.user is not None:
            if request.resolver_match.namespace == 'admin' or request.path_info.startswith('/admin/login'):
                if not request.user.is_staff and request.user.is_authenticated:
                    return HttpResponse(self.SSO_UNAUTHORISED_ACCESS_MESSAGE, status=401)
