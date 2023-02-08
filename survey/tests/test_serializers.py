import pytest

from survey.models import Choice
from survey.serializers import ChoiceSerializer
from survey.tests.factories import ChoiceFactory


@pytest.mark.django_db
def test_get_jump_field():
    for routing_choice in [Choice.END, Choice.JUMP, Choice.NO_ROUTING]:
        choice = ChoiceFactory(additional_routing=routing_choice)
        serializer = ChoiceSerializer(choice)

        jump_value = choice.question_to_jump_to.id if routing_choice == choice.JUMP else routing_choice
        assert serializer.data['jump'] == jump_value
