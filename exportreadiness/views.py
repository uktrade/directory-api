from rest_framework.generics import CreateAPIView, RetrieveAPIView
from . import mixins
from . import serializers


class TriageResultCreateRetrieveView(mixins.GetObjectOr404FromSSOIdMixin,
                                     CreateAPIView,
                                     RetrieveAPIView):
    serializer_class = serializers.TriageResultSerializer


class ArticleReadCreateRetrieveView(mixins.GetObjectOr404FromSSOIdMixin,
                                    CreateAPIView,
                                    RetrieveAPIView):
    serializer_class = serializers.ArticleReadSerializer


class TaskCompletedCreateRetrieveView(mixins.GetObjectOr404FromSSOIdMixin,
                                      CreateAPIView,
                                      RetrieveAPIView):
    serializer_class = serializers.TaskCompletedSerializer
