from enrolment import models


def test_trusted_source_signup_code_str():
    instance = models.TrustedSourceSignupCode(code='123456')

    assert str(instance) == '123456'
