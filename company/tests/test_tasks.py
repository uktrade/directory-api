from unittest import mock

from company.tasks import retrieve_companies_house_company_status


@mock.patch('company.tasks.lock_acquired', mock.Mock(return_value=True))
@mock.patch('company.tasks.call_command')
def retrieve_companies_house_company_status(mocked_call_command):
    retrieve_companies_house_company_status()
    mocked_call_command.assert_called_once_with(
        'retrieve_companies_house_company_status'
    )
