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
    field_names = User._meta.get_all_field_names()

    assert 'created' in field_names
    created_field = User._meta.get_field_by_name('created')[0]
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = User._meta.get_field_by_name('modified')[0]
    assert modified_field.__class__ is ModificationDateTimeField
