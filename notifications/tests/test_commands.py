from unittest.mock import patch

import pytest

from django.core.management import call_command
from django.core.management.base import CommandError


# TODO: Once the proper notification functions exist, check for those!
@patch('notifications.tests.mock_notify_func_daily1')
@patch('notifications.tests.mock_notify_func_daily2')
@patch('notifications.tests.mock_notify_func_weekly')
def test_notify_command_runs_functions_in_daily_type(
    mock_weekly, mock_daily2, mock_daily1, settings
):
    settings.DAILY_NOTIFICATIONS = [
        'notifications.tests.mock_notify_func_daily1',
        'notifications.tests.mock_notify_func_daily2',
    ]

    call_command('send_notifications', type='daily')

    assert mock_daily1.call_count == 1
    assert mock_daily2.call_count == 1
    assert mock_weekly.called is False


# TODO: Once the proper notification functions exist, check for those!
@patch('notifications.tests.mock_notify_func_daily1')
@patch('notifications.tests.mock_notify_func_daily2')
@patch('notifications.tests.mock_notify_func_weekly')
def test_notify_command_runs_functions_in_weekly_type(
    mock_weekly, mock_daily2, mock_daily1, settings
):
    settings.WEEKLY_NOTIFICATIONS = [
        'notifications.tests.mock_notify_func_weekly',
    ]

    call_command('send_notifications', type='weekly')

    assert mock_daily1.called is False
    assert mock_daily2.called is False
    assert mock_weekly.call_count == 1


def test_notify_command_handles_incorrect_type_param():
    with pytest.raises(CommandError):
        call_command('send_notifications', type='spam_mercilessly')


def test_notify_command_requires_type_param():
    with pytest.raises(CommandError):
        call_command('send_notifications')
