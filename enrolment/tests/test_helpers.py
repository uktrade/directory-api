from unittest.mock import Mock, patch

from enrolment import helpers


def test_generate_sms_verification_code():
    code = helpers.generate_sms_verification_code()

    assert code.isdigit()
    assert len(code) == 6
    assert code.lower() == code


@patch.object(helpers.NotificationsAPIClient, 'send_sms_notification',
              return_value=1)
@patch.object(helpers, 'generate_sms_verification_code',
              Mock(return_value='000000'))
def test_send_verification_code_via_sms(mock_send_sms_notification, settings):
    settings.GOV_NOTIFY_SERVICE_VERIFICATION_TEMPLATE_NAME = 'template'

    actual = helpers.send_verification_code_via_sms(12345)

    assert actual == '000000'
    mock_send_sms_notification.assert_called_once_with(
        12345,
        'template',
        personalisation={
            'verification_code': '000000',
        }
    )
