from unittest.mock import call, patch

from elasticsearch_dsl import Index
import pytest

from django.core.management import call_command


@patch('core.management.commands.distributed_migrate.MigrateCommand.handle')
@patch('core.management.commands.distributed_migrate.advisory_lock')
def test_distributed_migration(mocked_advisory_lock, mocked_handle):
    call_command('distributed_migrate')
    assert mocked_advisory_lock.call_args == call(
        lock_id='migrations', shared=False, wait=True
    )
    assert mocked_handle.call_count == 1


@pytest.mark.django_db
@pytest.mark.rebuild_elasticsearch
@patch('company.management.commands.populate_elasticsearch.Command.handle')
def test_ensure_elasticsearch_indices_exists(mock_handle, settings):
    call_command('ensure_elasticsearch_indices')

    assert mock_handle.call_count == 0


@pytest.mark.django_db
@pytest.mark.rebuild_elasticsearch
@patch('company.management.commands.populate_elasticsearch.Command.handle')
def test_ensure_elasticsearch_indices_not_exist(mock_handle, settings):
    Index(settings.ELASTICSEARCH_COMPANY_INDEX).delete()
    Index(settings.ELASTICSEARCH_CASE_STUDY_INDEX).delete()

    call_command('ensure_elasticsearch_indices')

    assert mock_handle.call_count == 1
