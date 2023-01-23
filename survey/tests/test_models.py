import pytest

from django.core.exceptions import ValidationError

from survey.models import Choice
from survey.tests.factories import ChoiceFactory


@pytest.mark.django_db
def test_error_raised_when_question_to_jump_to_required():
    '''Test that the correct validation error is raised when
    additional_routing is set to 'jump' but question_to_jump_to is empty'''
    choice = ChoiceFactory(additional_routing=Choice.JUMP)
    with pytest.raises(ValidationError) as exc_info:
        choice.clean_fields()
    assert exc_info.type is ValidationError
    assert exc_info.value.args[0]['question_to_jump_to'][0] == 'This field is required.'
