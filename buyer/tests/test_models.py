import pytest
from django_extensions.db.fields import CreationDateTimeField, ModificationDateTimeField

from buyer import models
from buyer.tests.factories import BuyerFactory


@pytest.mark.django_db
def test_buyer_name():
    buyer = BuyerFactory()
    assert str(buyer) == buyer.name


def test_buyer_model_has_update_create_timestamps():
    field_names = [field.name for field in models.Buyer._meta.get_fields()]

    assert 'created' in field_names
    created_field = models.Buyer._meta.get_field('created')
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = models.Buyer._meta.get_field('modified')
    assert modified_field.__class__ is ModificationDateTimeField
