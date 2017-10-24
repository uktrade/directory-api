from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from . import mixins
from . import serializers


class TriageResultCreateRetrieveView(
    mixins.GetObjectOr404FromSSOIdMixin, CreateAPIView, RetrieveAPIView,
    UpdateAPIView
):
    serializer_class = serializers.TriageResultSerializer


class ArticleReadCreateRetrieveView(mixins.FilterBySSOIdMixin,
                                    ListCreateAPIView):
    serializer_class = serializers.ArticleReadSerializer


class TaskCompletedCreateRetrieveView(mixins.FilterBySSOIdMixin,
                                      ListCreateAPIView):
    serializer_class = serializers.TaskCompletedSerializer
