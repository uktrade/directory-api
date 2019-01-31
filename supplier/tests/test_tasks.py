from unittest import mock

from supplier.tasks import suppliers_csv_upload


@mock.patch('supplier.tasks.lock_acquired', mock.Mock(return_value=True))
@mock.patch('supplier.tasks.call_command')
def test_suppliers_csv_upload(mocked_call_command):
    suppliers_csv_upload()
    mocked_call_command.assert_called_once_with(
        'generate_suppliers_csv_dump'
    )
