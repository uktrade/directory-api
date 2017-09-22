from unittest.mock import call, patch

# from directory_constants.constants import choices
import pytest

from exportopportunity.tests import factories


@pytest.mark.django_db
@patch('exportopportunity.signals.render_to_string', return_value='a message')
@patch('exportopportunity.signals.send_mail')
def test_email_france(mock_send_mail, mock_render_to_string, settings):
    settings.SUBJECT_EXPORT_OPPORTUNITY_CREATED = 'subject'
    settings.ITA_EMAILS_FOOD_IS_GREAT_FRANCE = ['france@example.com']
    settings.FAS_FROM_EMAIL = 'from@example.com'

    instance = factories.ExportOpportunityFactory(
        campaign='food-is-great',
        country='france',
    )

    assert mock_send_mail.call_count == 1
    assert mock_send_mail.call_args == call(
        subject='subject',
        message='a message',
        from_email='from@example.com',
        recipient_list=['france@example.com'],
    )

    assert mock_render_to_string.call_count == 1
    assert mock_render_to_string.call_args == call(
        'email/opportunity-submitted.txt', {'instance': instance}
    )


@pytest.mark.django_db
@patch('exportopportunity.signals.render_to_string', return_value='a message')
@patch('exportopportunity.signals.send_mail')
def test_email_singapore(mock_send_mail, mock_render_to_string, settings):
    settings.SUBJECT_EXPORT_OPPORTUNITY_CREATED = 'subject'
    settings.ITA_EMAILS_FOOD_IS_GREAT_SINGAPORE = ['singapore@example.com']
    settings.FAS_FROM_EMAIL = 'from@example.com'

    instance = factories.ExportOpportunityFactory(
        campaign='food-is-great',
        country='singapore',
    )

    assert mock_send_mail.call_count == 1
    assert mock_send_mail.call_args == call(
        subject='subject',
        message='a message',
        from_email='from@example.com',
        recipient_list=['singapore@example.com'],
    )

    assert mock_render_to_string.call_count == 1
    assert mock_render_to_string.call_args == call(
        'email/opportunity-submitted.txt', {'instance': instance}
    )
