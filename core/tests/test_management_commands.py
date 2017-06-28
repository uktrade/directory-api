from unittest.mock import patch

from django.core.management import call_command


@patch('core.management.commands.distributed_migrate.MigrateCommand.handle')
@patch('core.management.commands.distributed_migrate.advisory_lock')
def test_distributed_migration(mocked_advisory_lock, mocked_handle):
    call_command('distributed_migrate')
    mocked_advisory_lock.assert_called_once_with('migrations')
    assert mocked_handle.called
