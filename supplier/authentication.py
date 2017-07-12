from rest_framework import authentication, exceptions

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
        return self.authenticate_credentials(auth[1])

    def authenticate_credentials(self, session_id):
        response = helpers.sso_api_client.user.get_session_user(session_id)
        if not response.ok:
            raise exceptions.AuthenticationFailed(self.message_invalid_session)
        sso_data = response.json()
        sso_user = helpers.SSOUser(id=sso_data['id'], email=sso_data['email'])
        return (sso_user, session_id)

    def authenticate_header(self, request):
        return self.keyword


class Oauth2AuthenticationSSO(authentication.BaseAuthentication):
    message_invalid_session = 'Invalid bearer token'
    message_bad_format = 'Invalid bearer header.'
    keyword = 'Bearer'

    def authenticate(self, request):
        auth = authentication.get_authorization_header(request).split()
        if not auth or auth[0].decode() != self.keyword:
            return None
        if len(auth) == 1:
            raise exceptions.AuthenticationFailed(self.message_bad_format)
        return self.authenticate_credentials(auth[1])

    def authenticate_credentials(self, bearer_token):
        response = helpers.sso_api_client.user.get_oauth2_user_profile(
            bearer_token
        )
        if not response.ok:
            raise exceptions.AuthenticationFailed(self.message_invalid_session)

        sso_data = response.json()
        sso_user = helpers.SSOUser(id=sso_data['id'], email=sso_data['email'])
        return (sso_user, bearer_token)

    def authenticate_header(self, request):
        return self.keyword
