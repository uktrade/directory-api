from unittest import mock

import pytest
from django.core.management import call_command
from django.core.management.commands import migrate

from company.models import Company, CompanyUser
from company.tests.factories import CompanyFactory, CompanyUserFactory
from core.management.commands import distributed_migrate


@pytest.fixture()
def new_companies():
    return CompanyFactory.create_batch(10)


@pytest.fixture()
def new_suppliers():
    return CompanyUserFactory.create_batch(10)


@pytest.mark.django_db
def test_mask_data(new_companies, new_suppliers):
    call_command('mask_personal_data')

    for new_company in new_companies:
        masked_company = Company.objects.get(id=new_company.id)
        assert masked_company.postal_full_name != new_company.postal_full_name
        assert masked_company.address_line_1 != new_company.address_line_1
        assert masked_company.address_line_2 != new_company.address_line_2
        assert masked_company.postal_code != new_company.postal_code
        assert masked_company.po_box != new_company.po_box
        assert masked_company.email_address != new_company.email_address
        assert masked_company.email_full_name != new_company.email_full_name

    for new_supplier in new_suppliers:
        masked_supplier = CompanyUser.objects.get(id=new_supplier.id)
        assert masked_supplier.name != new_supplier.name
        assert masked_supplier.mobile_number != new_supplier.mobile_number
        assert masked_supplier.company_email != new_supplier.company_email


@pytest.mark.django_db
@mock.patch.object(migrate.Command, 'handle')
@mock.patch.object(distributed_migrate.Command, 'is_first_instance')
def test_distributed_migration_first(mock_is_first_instance, mock_handle):
    mock_is_first_instance.return_value = True

    call_command('distributed_migrate')

    assert mock_handle.call_count == 1


@pytest.mark.django_db
@mock.patch('time.sleep', mock.Mock)
@mock.patch.object(migrate.Command, 'handle')
@mock.patch.object(distributed_migrate.Command, 'is_migration_pending')
@mock.patch.object(distributed_migrate.Command, 'is_first_instance')
def test_distributed_migration_second(mock_is_first_instance, mock_is_migration_pending, mock_handle):
    mock_is_first_instance.return_value = False
    mock_is_migration_pending.side_effect = (
        True,
        False,
    )

    call_command('distributed_migrate')

    assert mock_handle.call_count == 0
