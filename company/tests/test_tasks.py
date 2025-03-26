from unittest import mock

import pytest

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
    mocked_call_command.assert_called_once_with('generate_company_users_csv_dump')


@mock.patch('company.management.commands.obsfucate_personal_details.Command.mask_company_user')
@pytest.mark.django_db
def test_obsfucate_personal_details(mock_mask_company_user):
    tasks.obsfucate_personal_details()
    assert mock_mask_company_user.call_count == 1
