from rest_framework.generics import RetrieveAPIView

from survey.models import Survey
from survey.serializers import SurveySerializer


class SurveyDetailView(RetrieveAPIView):
    """
    Get Survey by Id
    """

    permission_classes = []
    queryset = Survey.objects
    serializer_class = SurveySerializer
