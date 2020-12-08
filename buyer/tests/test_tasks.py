from unittest import mock

from buyer.tasks import buyers_csv_upload


@mock.patch('buyer.tasks.lock_acquired', mock.Mock(return_value=True))
@mock.patch('buyer.tasks.call_command')
def test_buyers_csv_upload(mocked_call_command):
    buyers_csv_upload()
    mocked_call_command.assert_called_once_with('generate_buyers_csv_dump')
