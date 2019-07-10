from django.core.exceptions import ValidationError
import environ

env = environ.Env()

NO_SELF_REDIRECT_ALLOWED_MESSAGE = 'Can not redirect to self.'
DOMAIN = env.str('DIRECTORY_CONSTANTS_URL_EXPORT_READINESS')


def self_redirect(target_url):
    if DOMAIN and DOMAIN in target_url.lower():
        raise ValidationError(NO_SELF_REDIRECT_ALLOWED_MESSAGE)
