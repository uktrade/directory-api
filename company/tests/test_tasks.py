from unittest import mock

import pytest
from django.test import override_settings

from company import tasks
from company.tests.factories import CompanyUserFactory


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


@override_settings(APP_ENVIRONMENT='dev')
@mock.patch('company.management.commands.obsfucate_personal_details.Command.mask_company_user')
@pytest.mark.django_db
def test_obsfucate_personal_details_lower_env(mock_mask_company_user):
    CompanyUserFactory()
    tasks.obsfucate_personal_details()
    assert mock_mask_company_user.call_count == 1


@override_settings(APP_ENVIRONMENT='production')
@mock.patch('company.management.commands.obsfucate_personal_details.Command.mask_company_user')
@pytest.mark.django_db
def test_obsfucate_personal_details_prod_env(mock_mask_company_user):
    CompanyUserFactory()
    tasks.obsfucate_personal_details()
    assert mock_mask_company_user.call_count == 0

