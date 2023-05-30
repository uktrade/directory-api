import pytest
from django.forms.models import inlineformset_factory

from survey.admin import ChoiceAdminForm, ChoiceInlineFormset
from survey.models import Choice, Question
from survey.tests.factories import ChoiceFactory, QuestionFactory


@pytest.mark.parametrize(
    'choice_2_additional_routing,expected_errors',
    (
        (Choice.NO_ROUTING, []),
        (
            Choice.END,
            [Choice.ADDITIONAL_ROUTING_ERROR],
        ),
        (
            Choice.JUMP,
            [Choice.ADDITIONAL_ROUTING_ERROR],
        ),
    ),
)
@pytest.mark.django_db
def test_choice_inline_form_validation(choice_2_additional_routing, expected_errors):
    question = QuestionFactory(type=Question.MULTI_SELECT)
    other_question = QuestionFactory()
    choice_1 = ChoiceFactory()
    choice_2 = ChoiceFactory()
    ChoiceFormSet = inlineformset_factory(
        Question,
        Choice,
        formset=ChoiceInlineFormset,
        fk_name='question',
        fields=['label', 'value', 'additional_routing', 'question_to_jump_to'],
        exclude=['id', 'modified', 'created', 'question'],
    )

    data = {
        'choices-TOTAL_FORMS': '2',
        'choices-INITIAL_FORMS': '2',
        'choices-MIN_NUM_FORMS': '0',
        'choices-MAX_NUM_FORMS': '1000',
        'choices-0-id': choice_1.id,
        'choices-0-question': question.id,
        'choices-0-label': 'choice 1',
        'choices-0-value': 'choice 1',
        'choices-0-additional_routing': 'end',
        'choices-0-question_to_jump_to': '',
        'choices-1-id': choice_2.id,
        'choices-1-question': question.id,
        'choices-1-label': 'choice 2',
        'choices-1-value': 'choice 2',
        'choices-1-additional_routing': choice_2_additional_routing,
        'choices-1-question_to_jump_to': '',
    }

    if choice_2_additional_routing == Choice.JUMP:
        data['choices-1-question_to_jump_to'] = other_question.id

    formset = ChoiceFormSet(data, instance=question, prefix='choices')
    assert formset.non_form_errors() == expected_errors


@pytest.mark.parametrize(
    'additional_routing,is_valid,', ((Choice.END, False), (Choice.JUMP, False), (Choice.NO_ROUTING, True))
)
@pytest.mark.django_db
def test_choice_admin_form_validation(additional_routing, is_valid):
    question = QuestionFactory(type=Question.MULTI_SELECT)
    other_question = QuestionFactory()
    ChoiceFactory(question=question, additional_routing=Choice.END)
    data = {
        'question': str(question.id),
        'label': 'A choice',
        'value': 'A choice',
        'additional_routing': additional_routing,
        'question_to_jump_to': '',
    }

    if additional_routing == Choice.JUMP:
        data['question_to_jump_to'] = str(other_question.id)

    form = ChoiceAdminForm(data)

    assert form.is_valid() == is_valid
    if not is_valid:
        assert form.errors['additional_routing'][0] == Choice.ADDITIONAL_ROUTING_ERROR
