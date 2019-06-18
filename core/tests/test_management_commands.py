from unittest.mock import call, patch

import pytest

from django.core.management import call_command
from company.tests.factories import CompanyFactory
from supplier.tests.factories import SupplierFactory

from company.models import Company
from supplier.models import Supplier


@pytest.fixture()
def new_companies():
    new_companies = []
    for _ in range(10):
        new_companies.append(
            CompanyFactory()
        )
    return new_companies


@pytest.fixture()
def new_suppliers():
    new_suppliers = []
    for _ in range(10):
        new_suppliers.append(
            SupplierFactory()
        )
    return new_suppliers


@patch('core.management.commands.distributed_migrate.MigrateCommand.handle')
@patch('core.management.commands.helpers.advisory_lock')
def test_distributed_migration(mocked_advisory_lock, mocked_handle):
    call_command('distributed_migrate')
    assert mocked_handle.call_count == 1
    assert mocked_advisory_lock.call_args == call(
        lock_id='migrations', wait=False,
    )


@pytest.mark.django_db
@patch(
    'core.management.commands.distributed_elasticsearch_migrate.'
    'MigrateCommand.handle'
)
@patch(
    'core.management.commands.helpers.advisory_lock'
)
def test_distributed_migration_elasticsearch(
    mocked_advisory_lock, mocked_handle
):
    call_command('distributed_elasticsearch_migrate')
    assert mocked_handle.call_count == 1
    assert mocked_advisory_lock.call_args == call(
        lock_id='es_migrations', wait=False,
    )


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
        masked_supplier = Supplier.objects.get(id=new_supplier.id)
        assert masked_supplier.name != new_supplier.name
        assert masked_supplier.company_email != new_supplier.company_email
