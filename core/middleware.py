import sigauth.middleware

from django.conf import settings


class SignatureCheckMiddleware(
    sigauth.middleware.SignatureCheckMiddlewareBase
):
    secret = settings.SIGNATURE_SECRET

    def should_check(self, request):
        if request.resolver_match.namespace in ['admin', 'healthcheck']:
            return False
        return super().should_check(request)
