from enrolment import constants
from enrolment.templatetags.enrolment_email import email_image


def test_email_image_returns_constant_image():
    assert email_image('a') == constants.EMAIL_STATIC_FILE_BUCKET + 'a'
