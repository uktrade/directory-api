from unittest.mock import patch

from api.distributed_lock import distributed_lock


@patch(
    'api.distributed_lock.distributed_lock_manager.lock', return_value=False
)
def test_distributed_lock_not_acquired(mock_distributed_lock_manager):
    """Tests that the context manager is not raising exceptions when lock was
    not acquired
    """
    with distributed_lock('test') as lock_acquired:
        assert lock_acquired is False
