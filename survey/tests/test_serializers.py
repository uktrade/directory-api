import pytest

from survey.models import Choice
from survey.serializers import ChoiceSerializer
from survey.tests.factories import ChoiceFactory


@pytest.mark.django_db
def test_get_jump_field():
    for routing_choice in [Choice.JUMP, Choice.NO_ROUTING, Choice.END]:
        choice = ChoiceFactory(additional_routing=routing_choice)
        serializer = ChoiceSerializer(choice)
        jump_value = choice.question_to_jump_to.id if choice.question_to_jump_to else routing_choice

        assert serializer.data['jump'] == jump_value
