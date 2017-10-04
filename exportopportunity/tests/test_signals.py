from unittest.mock import call, patch

import pytest
from directory_constants.constants import lead_generation

from exportopportunity.tests import factories


@pytest.mark.django_db
@patch('exportopportunity.signals.render_to_string', return_value='a message')
@patch('exportopportunity.signals.send_mail')
@pytest.mark.parametrize('country,campaign,email', [
    [lead_generation.FRANCE,    lead_generation.FOOD_IS_GREAT, 'food@f.co'],
    [lead_generation.SINGAPORE, lead_generation.FOOD_IS_GREAT, 'food@s.co'],
    [lead_generation.FRANCE,    lead_generation.LEGAL_IS_GREAT, 'legal@f.co'],
    [lead_generation.SINGAPORE, lead_generation.LEGAL_IS_GREAT, 'legal@s.co'],
])
def test_email(
    mock_send_mail, mock_render_to_string, settings, country, campaign, email
):
    settings.SUBJECT_EXPORT_OPPORTUNITY_CREATED = 'subject'
    settings.ITA_EMAILS_FOOD_IS_GREAT_FRANCE = ['food@f.co']
    settings.ITA_EMAILS_FOOD_IS_GREAT_SINGAPORE = ['food@s.co']
    settings.ITA_EMAILS_LEGAL_IS_GREAT_FRANCE = ['legal@f.co']
    settings.ITA_EMAILS_LEGAL_IS_GREAT_SINGAPORE = ['legal@s.co']
    settings.FAS_FROM_EMAIL = 'from@example.com'

    instance = factories.ExportOpportunityFactory(
        campaign=campaign, country=country,
    )

    assert mock_send_mail.call_count == 1
    assert mock_send_mail.call_args == call(
        subject='subject',
        message='a message',
        from_email='from@example.com',
        recipient_list=[email],
    )

    assert mock_render_to_string.call_count == 1
    assert mock_render_to_string.call_args == call(
        'email/opportunity-submitted.txt', {'instance': instance}
    )
