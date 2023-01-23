import pytest

from survey.models import Choice
from survey.serializers import ChoiceSerializer
from survey.tests.factories import ChoiceFactory, QuestionFactory


@pytest.mark.django_db
def test_get_jump_field():
    question = QuestionFactory()
    choice = ChoiceFactory(question=question, additional_routing=Choice.JUMP, question_to_jump_to=question)

    data = {
        "label": choice.label,
        "value": choice.value,
        "additional_routing": choice.additional_routing,
        "question_to_jump_to": question.id,
    }
    serializer = ChoiceSerializer(data=data)
    assert serializer.is_valid() is True
    choice = serializer.save()
    assert choice.jump == question.id
