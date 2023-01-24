from rest_framework.serializers import ModelSerializer, SerializerMethodField

from survey.models import Choice, Question, Survey


class ChoiceSerializer(ModelSerializer):
    jump = SerializerMethodField()

    class Meta:
        model = Choice
        fields = (
            'label',
            'value',
            'jump',
        )

    def get_jump(self, obj):
        if obj.additional_routing == Choice.JUMP:
            return obj.question_to_jump_to.id

        return obj.additional_routing


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
