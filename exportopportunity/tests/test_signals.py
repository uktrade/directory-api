from unittest.mock import call, patch

# from directory_constants.constants import choices
import pytest

from exportopportunity.tests import factories


@pytest.mark.django_db
@patch('exportopportunity.signals.render_to_string', return_value='a message')
@patch('exportopportunity.signals.send_mail')
def test_sends_email(mock_send_mail, mock_render_to_string, settings):
    settings.SUBJECT_EXPORT_OPPORTUNITY_CREATED = 'subject'
    settings.RECIPIENT_EMAIL_EXPORT_OPPORTUNITY_CREATED = 'to@example.com'
    settings.FAS_FROM_EMAIL = 'from@example.com'

    instance = factories.ExportOpportunityFactory()

    assert mock_send_mail.call_count == 1
    assert mock_send_mail.call_args == call(
        subject='subject',
        message='a message',
        from_email='from@example.com',
        recipient_list=('to@example.com',),
    )

    assert mock_render_to_string.call_count == 1
    assert mock_render_to_string.call_args == call(
        'email/opportunity-submitted.txt', {'opportunity': instance}
    )
