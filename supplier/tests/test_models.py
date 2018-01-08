import pytest

from django_extensions.db.fields import (
    ModificationDateTimeField, CreationDateTimeField
)

from supplier.models import Supplier
from supplier.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_supplier_model_str():
    supplier = Supplier(**VALID_REQUEST_DATA)

    assert supplier.company_email == str(supplier)


def test_user_model_has_update_create_timestamps():
    field_names = [field.name for field in Supplier._meta.get_fields()]

    assert 'created' in field_names
    created_field = Supplier._meta.get_field('created')
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = Supplier._meta.get_field('modified')
    assert modified_field.__class__ is ModificationDateTimeField
