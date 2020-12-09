import pytest
from django.db.utils import IntegrityError

from enrolment import models
from enrolment.tests import factories


def test_trusted_source_signup_code_str():
    instance = models.PreVerifiedEnrolment(company_number='12345678', email_address='jim@example.com')

    assert str(instance) == '12345678'


@pytest.mark.django_db
def test_unique_together():
    factories.PreVerifiedEnrolmentFactory(company_number='1111111', email_address='1@a.com')

    with pytest.raises(IntegrityError):
        factories.PreVerifiedEnrolmentFactory(company_number='1111111', email_address='1@a.com')
