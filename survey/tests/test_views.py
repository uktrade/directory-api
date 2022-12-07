import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from survey.tests.factories import ChoiceFactory, QuestionFactory, SurveyFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_get_survey_not_found(api_client):
    url = reverse('retrieve-survey', kwargs={'pk': 123})
    response = api_client.get(url)

    assert response.status_code == 404


@pytest.mark.django_db
def test_get_survey_success(api_client):
    survey = SurveyFactory.create()
    question = QuestionFactory.create(survey=survey)
    choice = ChoiceFactory.create(question=question)

    url = reverse('retrieve-survey', kwargs={'pk': survey.id})
    response = api_client.get(url)
    data = response.json()

    assert response.status_code == 200
    assert data["id"] == str(survey.id)
    assert data["name"] == survey.name

    assert len(data["questions"]) == 1
    assert data["questions"][0]["id"] == question.id
    assert data["questions"][0]["order"] == question.order
    assert data["questions"][0]["title"] == question.title
    assert data["questions"][0]["type"] == question.type
    assert data["questions"][0]["add_other_option"] == question.add_other_option

    assert len(data["questions"][0]["choices"]) == 1
    assert data["questions"][0]["choices"][0]["label"] == choice.label
    assert data["questions"][0]["choices"][0]["value"] == choice.value
    assert data["questions"][0]["choices"][0]["jump"] == choice.jump
