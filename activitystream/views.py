import logging

from django.conf import settings
from django.core.cache import cache
from django.utils.crypto import constant_time_compare
from django.utils.decorators import decorator_from_middleware
from mohawk import Receiver
from mohawk.exc import HawkFail
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


logger = logging.getLogger(__name__)

NO_CREDENTIALS_MESSAGE = 'Authentication credentials were not provided.'
INCORRECT_CREDENTIALS_MESSAGE = 'Incorrect authentication credentials.'


def lookup_credentials(access_key_id):
    """Raises a HawkFail if the passed ID is not equal to
    settings.ACTIVITY_STREAM_ACCESS_KEY_ID
    """
    if not constant_time_compare(access_key_id,
                                 settings.ACTIVITY_STREAM_ACCESS_KEY_ID):
        raise HawkFail('No Hawk ID of {access_key_id}'.format(
            access_key_id=access_key_id,
        ))

    return {
        'id': settings.ACTIVITY_STREAM_ACCESS_KEY_ID,
        'key': settings.ACTIVITY_STREAM_SECRET_ACCESS_KEY,
        'algorithm': 'sha256',
    }


def seen_nonce(access_key_id, nonce, _):
    """Returns if the passed access_key_id/nonce combination has been
    used within 60 seconds
    """
    cache_key = 'activity_stream:{access_key_id}:{nonce}'.format(
        access_key_id=access_key_id,
        nonce=nonce,
    )

    # cache.add only adds key if it isn't present
    seen_cache_key = not cache.add(
        cache_key, True, timeout=60,
    )

    if seen_cache_key:
        logger.warning('Already seen nonce {nonce}'.format(nonce=nonce))

    return seen_cache_key


def authorise(request):
    """Raises a HawkFail if the passed request cannot be authenticated"""
    return Receiver(
        lookup_credentials,
        request.META['HTTP_AUTHORIZATION'],
        request.build_absolute_uri(),
        request.method,
        content=request.body,
        content_type=request.content_type,
        seen_nonce=seen_nonce,
    )


class ActivityStreamAuthentication(BaseAuthentication):

    def authenticate_header(self, request):
        """This is returned as the WWW-Authenticate header when
        AuthenticationFailed is raised. DRF also requires this
        to send a 401 (as opposed to 403)
        """
        return 'Hawk'

    def authenticate(self, request):
        """Authenticates a request using two mechanisms:

        1. The X-Forwarded-For-Header, compared against a whitelist
        2. A Hawk signature in the Authorization header

        If either of these suggest we cannot authenticate, AuthenticationFailed
        is raised, as required in the DRF authentication flow
        """
        self.authenticate_by_ip(request)
        return self.authenticate_by_hawk(request)

    def authenticate_by_ip(self, request):
        if 'HTTP_X_FORWARDED_FOR' not in request.META:
            logger.warning(
                'Failed authentication: no X-Forwarded-For header passed'
            )
            raise AuthenticationFailed(INCORRECT_CREDENTIALS_MESSAGE)

        x_forwarded_for = request.META['HTTP_X_FORWARDED_FOR']
        ip_addesses = x_forwarded_for.split(',')
        if len(ip_addesses) < 2:
            logger.warning(
                'Failed authentication: the X-Forwarded-For header does not '
                'contain enough IP addresses'
            )
            raise AuthenticationFailed(INCORRECT_CREDENTIALS_MESSAGE)

        # PaaS appends 2 IPs, where the IP connected from is the first
        remote_address = ip_addesses[-2].strip()

        if remote_address not in settings.ACTIVITY_STREAM_IP_WHITELIST:
            logger.warning(
                'Failed authentication: the X-Forwarded-For header was not '
                'produced by a whitelisted IP'
            )
            raise AuthenticationFailed(INCORRECT_CREDENTIALS_MESSAGE)

    def authenticate_by_hawk(self, request):
        if 'HTTP_AUTHORIZATION' not in request.META:
            raise AuthenticationFailed(NO_CREDENTIALS_MESSAGE)

        try:
            hawk_receiver = authorise(request)
        except HawkFail as e:
            logger.warning('Failed authentication {e}'.format(
                e=e,
            ))
            raise AuthenticationFailed(INCORRECT_CREDENTIALS_MESSAGE)

        return (None, hawk_receiver)


class ActivityStreamHawkResponseMiddleware:
    """Adds the Server-Authorization header to the response, so the originator
    of the request can authenticate the response
    """

    def process_response(self, viewset, response):
        """Adds the Server-Authorization header to the response, so the originator
        of the request can authenticate the response
        """
        response['Server-Authorization'] = viewset.request.auth.respond(
            content=response.content,
            content_type=response['Content-Type'],
        )
        return response


class ActivityStreamViewSet(ViewSet):
    """List-only view set for the activity stream"""

    authentication_classes = (ActivityStreamAuthentication,)
    permission_classes = ()

    @decorator_from_middleware(ActivityStreamHawkResponseMiddleware)
    def list(self, request):
        """A single page of activities"""
        return Response({'secret': 'content-for-pen-test'})
