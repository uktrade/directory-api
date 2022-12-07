from rest_framework.serializers import ModelSerializer

from survey.models import Choice, Question, Survey


class ChoiceSerializer(ModelSerializer):
    class Meta:
        model = Choice
        fields = (
            'label',
            'value',
            'jump',
        )


class QuestionSerializer(ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ('id', 'order', 'title', 'type', 'add_other_option', 'choices')
        depth = 1


class SurveySerializer(ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Survey
        fields = ('id', 'name', 'created', 'modified', 'questions')
        depth = 2
