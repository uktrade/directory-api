import pytest

from django_extensions.db.fields import (
    ModificationDateTimeField, CreationDateTimeField
)

from user.models import User
from user.tests import VALID_REQUEST_DATA


@pytest.mark.django_db
def test_user_model_str():
    user = User(**VALID_REQUEST_DATA)

    assert user.company_email == str(user)


def test_user_model_has_update_create_timestamps():
    field_names = [field.name for field in User._meta.get_fields()]

    assert 'created' in field_names
    created_field = User._meta.get_field('created')
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = User._meta.get_field('modified')
    assert modified_field.__class__ is ModificationDateTimeField
