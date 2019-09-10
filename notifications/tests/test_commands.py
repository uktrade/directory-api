from unittest.mock import patch

import pytest

from django.core.management import call_command
from django.core.management.base import CommandError


@patch('notifications.notifications.hasnt_logged_in')
@patch('notifications.notifications.verification_code_not_given')
@patch('notifications.notifications.new_companies_in_sector')
def test_notify_command_runs_functions_in_daily_type(
    mock_new_companies, mock_verify_code, mock_login
):
    call_command('send_notifications', type='daily')

    assert mock_verify_code.call_count == 1
    assert mock_login.call_count == 1
    assert mock_new_companies.called is False


@patch('notifications.notifications.hasnt_logged_in')
@patch('notifications.notifications.verification_code_not_given')
@patch('notifications.notifications.new_companies_in_sector')
def test_notify_command_runs_functions_in_weekly_type(
    mock_new_companies, mock_verify_code, mock_login
):
    call_command('send_notifications', type='weekly')

    assert mock_verify_code.called is False
    assert mock_login.called is False
    assert mock_new_companies.call_count == 1


def test_notify_command_handles_incorrect_type_param():
    with pytest.raises(CommandError):
        call_command('send_notifications', type='spam_mercilessly')


def test_notify_command_requires_type_param():
    with pytest.raises(CommandError):
        call_command('send_notifications')
