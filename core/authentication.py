from directory_sso_api_client.client import sso_api_client
from rest_framework import authentication, exceptions
from rest_framework.authentication import BasicAuthentication

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.crypto import constant_time_compare

from supplier import helpers


class SessionAuthenticationSSO(authentication.BaseAuthentication):
    """
    Clients should authenticate by passing the sso session id in the
    "Authorization" HTTP header, prepended with the string "SSO_SESSION_ID ".
    For example:
        Authorization: SSO_SESSION_ID 401f7ac837da42b97f613d789819ff93537bee6a
    """

    message_invalid_session = 'Invalid session id'
    message_bad_format = 'Invalid SSO_SESSION_ID header.'
    keyword = 'SSO_SESSION_ID'

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        if not auth or auth[0].decode() != self.keyword:
            return None
        if len(auth) == 1:
            raise exceptions.AuthenticationFailed(self.message_bad_format)
        return self.authenticate_credentials(auth[1].decode())

    def authenticate_credentials(self, session_id):
        response = sso_api_client.user.get_session_user(session_id)
        if not response.ok:
            raise exceptions.AuthenticationFailed(self.message_invalid_session)
        sso_data = response.json()
        sso_user = helpers.SSOUser(
            id=sso_data['id'],
            email=sso_data['email']
        )
        return (sso_user, session_id)

    def authenticate_header(self, request):
        return self.keyword


class Oauth2AuthenticationSSO(authentication.BaseAuthentication):
    """
    Clients should authenticate by passing an oauth2 bearer token in the
    "Authorization" HTTP header, prepended with the string "Bearer ".
    For example:
        Authorization: Bearer th38ear3rt0k3n
    """

    message_invalid_session = 'Invalid bearer token'
    message_bad_format = 'Invalid bearer header.'
    keyword = 'Bearer'

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        if not auth or auth[0].decode() != self.keyword:
            return None
        if len(auth) == 1:
            raise exceptions.AuthenticationFailed(self.message_bad_format)
        return self.authenticate_credentials(auth[1].decode())

    def authenticate_credentials(self, bearer_token):
        response = sso_api_client.user.get_oauth2_user_profile(
            bearer_token
        )
        if not response.ok:
            raise exceptions.AuthenticationFailed(self.message_invalid_session)

        sso_data = response.json()
        sso_user = helpers.SSOUser(id=sso_data['id'], email=sso_data['email'])
        return (sso_user, bearer_token)

    def authenticate_header(self, request):
        return self.keyword


class GeckoBasicAuthentication(BasicAuthentication):
    """Authentication class that uses a username and password setting
    instead of a django user

    DRF's BasicAuthentication class uses the auth.User model for
    authentication. Credentials created for gecko could therefore
    be used to access other parts of the site. The purpose of this
    class is to give gecko access to just views that use this
    class and absolutely nothing else."""

    def authenticate_credentials(self, userid, password, request=None):
        username_ok = constant_time_compare(userid, settings.GECKO_API_KEY)
        password_ok = constant_time_compare(password, settings.GECKO_API_PASS)
        if username_ok and password_ok:
            user = User(username=userid)
            return (user, None)
        else:
            raise exceptions.AuthenticationFailed('Invalid username/password.')
