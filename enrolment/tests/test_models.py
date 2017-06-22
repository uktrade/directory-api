import pytest
from django.core.signing import Signer

from enrolment import models
from enrolment.tests import factories


def test_trusted_source_signup_code_str():
    instance = models.TrustedSourceSignupCode(code='123456')

    assert str(instance) == '123456'


@pytest.mark.django_db
def test_trusted_source_signup_code_generates_code_on_create():
    code = factories.TrustedSourceSignupCodeFactory.create(
        email_address='fred@example.com'
    )

    assert Signer().unsign(code.code) == 'fred@example.com'


@pytest.mark.django_db
def test_trusted_source_signup_code_not_generates_code_on_update():
    code = factories.TrustedSourceSignupCodeFactory.create(
        email_address='fred@example.com'
    )

    value_before_update = code.code
    code.save()
    code.refresh_from_db()

    assert code.code == value_before_update


@pytest.mark.django_db
def test_trusted_source_signup_code_enrolment_link(settings):
    settings.FAB_TRUSTED_SOURCE_ENROLMENT_LINK = 'http://thing.com/{code}/'
    code = factories.TrustedSourceSignupCodeFactory.build(
        code='123'
    )
    assert code.enrolment_link == 'http://thing.com/123/'
