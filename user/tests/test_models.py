import pytest
from directory_constants import user_roles

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


@pytest.mark.django_db
def test_user_model_is_company_owner_true():
    user = User(**VALID_REQUEST_DATA)
    user.role = user_roles.ADMIN
    assert user.is_company_owner is True


@pytest.mark.django_db
def test_user_model_is_company_owner_False():
    user = User(**VALID_REQUEST_DATA)
    user.role = user_roles.EDITOR
    assert user.is_company_owner is False
    user.role = user_roles.MEMBER
    assert user.is_company_owner is False
