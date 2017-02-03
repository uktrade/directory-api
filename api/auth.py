from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from rest_framework import exceptions
from rest_framework.authentication import BasicAuthentication


class GeckoBasicAuthentication(BasicAuthentication):
    """Authentication class that uses a username and password setting
    instead of a django user

    DRF's BasicAuthentication class uses the auth.User model for
    authentication. Credentials created for gecko could therefore
    be used to access other parts of the site. The purpose of this
    class is to give gecko access to just views that use this
    class and absolutely nothing else."""

    def authenticate_credentials(self, userid, password):
        username_invalid = (userid != settings.GECKO_API_KEY)
        password_invalid = (password != settings.GECKO_API_PASS)
        if username_invalid or password_invalid:
            raise exceptions.AuthenticationFailed(
                _('Invalid username/password.'))
        else:
            user = User(username=userid)

        return (user, None)
