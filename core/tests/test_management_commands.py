from unittest.mock import call, patch

from django.core.management import call_command


@patch('core.management.commands.distributed_migrate.MigrateCommand.handle')
@patch('core.management.commands.distributed_migrate.advisory_lock')
def test_distributed_migration(mocked_advisory_lock, mocked_handle):
    call_command('distributed_migrate')
    assert mocked_advisory_lock.call_args == call(
        lock_id='migrations', shared=False, wait=True
    )
    assert mocked_handle.call_count == 1
