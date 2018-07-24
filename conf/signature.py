from sigauth import middleware

from django.conf import settings


class SignatureCheckMiddleware(middleware.SignatureCheckMiddlewareBase):
    secret = settings.SIGNATURE_SECRET
