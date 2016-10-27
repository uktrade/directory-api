from unittest.mock import Mock, patch

from enrolment import helpers


def test_generate_sms_verification_code():
    actual = helpers.generate_sms_verification_code()

    assert len(actual) == 6
    assert actual.lower() == actual


@patch.object(helpers.NotificationsAPIClient, 'send_sms_notification',
              return_value=1)
@patch.object(helpers, 'generate_sms_verification_code',
              Mock(return_value='ABCDEF'))
def test_send_verification_code_via_sms(mock_send_sms_notification, settings):
    settings.GOV_NOTIFY_SERVICE_VERIFICATION_TEMPLATE_NAME = 'template'
    settings.GOV_NOTIFY_SERVICE_NAME = 'name'

    actual = helpers.send_verification_code_via_sms(12345)

    assert actual == 'ABCDEF'
    mock_send_sms_notification.assert_called_once_with(
        12345,
        'template',
        personalisation={
            'service_name': 'name',
            'verification_code': 'ABCDEF',
        }
    )
