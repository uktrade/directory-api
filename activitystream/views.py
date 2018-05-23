import logging

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from mohawk import Receiver
from mohawk.exc import HawkFail
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

log = logging.getLogger(__name__)

NOT_PROVIDED = 'Authentication credentials were not provided.'
INCORRECT = 'Incorrect authentication credentials.'


def lookup_credentials(access_key_id):
    if access_key_id != settings.ACTIVITY_STREAM_ACCESS_KEY_ID:
        raise AuthenticationFailed(
            'No Hawk ID of {access_key_id}'.format(id=access_key_id)
        )

    return {
        'id': settings.ACTIVITY_STREAM_ACCESS_KEY_ID,
        'key': settings.ACTIVITY_STREAM_SECRET_ACCESS_KEY,
        'algorithm': 'sha256',
    }


def seen_nonce(access_key_id, nonce, _):
    # This is a reason to _not_ use HawkRest: its nonce cache key
    # contains a timestamp but it shouldn't, since the same nonce
    # on a different timestamp should be rejected.
    cache_key = 'activity_stream:{access_key_id}:{nonce}'.format(
        access_key_id=access_key_id, nonce=nonce)
    seen_cache_key = cache.get(cache_key, False)

    # cache.add only adds key if it isn't present
    cache.add(cache_key, True, timeout=60)

    if seen_cache_key:
        log.warning('Already seen nonce {nonce}'.format(nonce=nonce))

    return seen_cache_key


def raise_exception_if_not_authentic(request):
    Receiver(
        lookup_credentials,
        request.META['HTTP_AUTHORIZATION'],
        request.build_absolute_uri(),
        request.method,
        content=request.body,
        content_type=request.content_type,
        seen_nonce=seen_nonce,
    )


class ActivityStreamUser(AnonymousUser):
    username = 'activity_stream_user'

    @property
    def is_authenticated(self):
        return True


class ActivityStreamAuthentication(BaseAuthentication):

    # This is returned as the WWW-Authenticate header when
    # AuthenticationFailed is raised. DRF also requires this
    # to send a 401 (as opposed to 403)
    def authenticate_header(self, request):
        return 'Hawk'

    def authenticate(self, request):
        if 'HTTP_X_FORWARDED_FOR' not in request.META:
            log.warning(
                'Failed authentication: no X-Forwarded-For header passed'
            )
            raise AuthenticationFailed(INCORRECT)

        remote_address = \
            request.META['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()

        if remote_address not in ['1.2.3.4', '2.3.4.5']:
            log.warning(
                'Failed authentication: the X-Forwarded-For header did not '
                'start with an IP in the whitelist'
            )
            raise AuthenticationFailed(INCORRECT)

        if 'HTTP_AUTHORIZATION' not in request.META:
            raise AuthenticationFailed(NOT_PROVIDED)

        try:
            raise_exception_if_not_authentic(request)
        except HawkFail as e:
            log.warning('Failed authentication {}'.format(e))
            raise AuthenticationFailed(INCORRECT)

        return (ActivityStreamUser(), None)


class ActivityStreamViewSet(ViewSet):
    authentication_classes = (ActivityStreamAuthentication,)
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        return Response({"secret": "content-for-pen-test"})
