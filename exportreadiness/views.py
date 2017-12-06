from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    UpdateAPIView)

from core import authentication
from . import mixins
from . import serializers


class TriageResultCreateRetrieveView(
    mixins.GetObjectOr404FromSSOIdMixin, CreateAPIView, RetrieveAPIView,
    UpdateAPIView
):
    serializer_class = serializers.TriageResultSerializer


class TriageResultRetrieveExternalAPIView(
    mixins.GetObjectOr404FromSSOIdMixin, RetrieveAPIView
):
    serializer_class = serializers.TriageResultSerializer
    authentication_classes = [
        authentication.Oauth2AuthenticationSSO,
        authentication.SessionAuthenticationSSO,
    ]


class ArticleReadCreateRetrieveView(mixins.FilterBySSOIdMixin,
                                    ListCreateAPIView):
    serializer_class = serializers.ArticleReadSerializer


class TaskCompletedCreateRetrieveView(mixins.FilterBySSOIdMixin,
                                      ListCreateAPIView):
    serializer_class = serializers.TaskCompletedSerializer
