import pytest

from django.core.exceptions import ValidationError

from redirects import validators
from redirects.tests.factories import RedirectFactory
import environ

env = environ.Env()


@pytest.mark.django_db
def test_self_redirect_valid_input(client):
    redirects = RedirectFactory()
    try:
        validators.self_redirect(redirects.target_url)
    except ValidationError:
        pytest.fail('Redirect should only fail if its redirecting to a substring of '
                    'DIRECTORY_CONSTANTS_URL_EXPORT_READINESS, meaning that it redirects '
                    'back to our production domain, potentially creating a loop')


@pytest.mark.django_db
def test_self_redirect_invalid_input(client):
    with pytest.raises(ValidationError):
        validators.self_redirect(env.str('DIRECTORY_CONSTANTS_URL_EXPORT_READINESS'))
