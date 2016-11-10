from enrolment.templatetags.enrolment_email import header_image
from enrolment import constants


def test_header_image_returns_constant_image():
    assert header_image() == constants.EMAIL_HEADER_IMAGE
