import factory

from survey.models import Choice, Question, Survey


class SurveyFactory(factory.django.DjangoModelFactory):
    name = factory.Sequence(lambda n: f'Survey {n}')

    class Meta:
        model = Survey


class QuestionFactory(factory.django.DjangoModelFactory):
    title = factory.fuzzy.FuzzyText(length=12)
    survey = factory.SubFactory(SurveyFactory)
    type = factory.fuzzy.FuzzyChoice([i[0] for i in Question.QUESTION_TYPE_CHOICES])
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = Question


class ChoiceFactory(factory.django.DjangoModelFactory):
    label = factory.fuzzy.FuzzyText(length=12)
    value = factory.fuzzy.FuzzyText(length=12)
    question = factory.SubFactory(QuestionFactory)

    class Meta:
        model = Choice
