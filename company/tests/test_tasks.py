from unittest import mock

from company import tasks


@mock.patch('company.tasks.lock_acquired', mock.Mock(return_value=True))
@mock.patch('company.tasks.call_command')
def test_retrieve_companies_house_company_status(mocked_call_command):
    tasks.retrieve_companies_house_company_status()
    mocked_call_command.assert_called_once_with('retrieve_companies_house_company_status')


@mock.patch('company.tasks.lock_acquired', mock.Mock(return_value=True))
@mock.patch('company.tasks.call_command')
def test_suppliers_csv_upload(mocked_call_command):
    tasks.suppliers_csv_upload()
    mocked_call_command.assert_called_once_with('generate_suppliers_csv_dump')
