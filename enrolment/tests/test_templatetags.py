from django.test import override_settings

from enrolment.templatetags.enrolment_email import email_image


@override_settings(AWS_STORAGE_BUCKET_NAME_EMAIL='aws_bucket_name')
def test_email_image_returns_constant_image():
    assert email_image('EiG-logo-email.png') == 'https://aws_bucket_name.s3.amazonaws.com/EiG-logo-email.png'
