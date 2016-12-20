from django_extensions.db.fields import (
    ModificationDateTimeField, CreationDateTimeField
)

from enrolment.models import Enrolment


def test_enrolment_model_has_update_create_timestamps():
    field_names = [field.name for field in Enrolment._meta.get_fields()]

    assert 'created' in field_names
    created_field = Enrolment._meta.get_field_by_name('created')[0]
    assert created_field.__class__ is CreationDateTimeField

    assert 'modified' in field_names
    modified_field = Enrolment._meta.get_field_by_name('modified')[0]
    assert modified_field.__class__ is ModificationDateTimeField
