import pytest
from django.core.exceptions import ValidationError

from survey.models import Choice
from survey.tests.factories import ChoiceFactory, QuestionFactory, SurveyFactory


@pytest.mark.parametrize(
    'model_factory,attr_used_as_str',
    ((SurveyFactory, 'name'), (QuestionFactory, 'title')),
)
@pytest.mark.django_db
def test_model_to_string(model_factory, attr_used_as_str):
    instance = model_factory()
    assert str(instance) == getattr(instance, attr_used_as_str)


@pytest.mark.django_db
def test_choice_clean_fields_error_raised():
    '''Test that the correct validation error is raised when
    additional_routing is set to 'jump' but question_to_jump_to is empty'''
    choice = ChoiceFactory(additional_routing=Choice.JUMP, question_to_jump_to=None)
    with pytest.raises(ValidationError) as exc_info:
        choice.clean_fields()
    assert exc_info.type is ValidationError
    assert exc_info.value.args[0]['question_to_jump_to'][0] == 'This field is required.'


@pytest.mark.django_db
def test_choice_clean_fields_success():
    '''Test that clean_fields is successful if additional_routing is set to 'jump'
    and a question object is provided to question_to_jump_to'''
    question = QuestionFactory()
    choice = ChoiceFactory(additional_routing=Choice.JUMP, question_to_jump_to=question)
    try:
        choice.clean_fields()
    except Exception as exc:
        assert False, f"'clean_fields' raised an exception {exc}"
