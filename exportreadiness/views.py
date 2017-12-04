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

    def get_serializer(self, *args, **kwargs):
        # allow bulk creating articles read for performance gains: ED-2822
        if isinstance(kwargs.get('data'), list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def create(self, *args, **kwargs):
        super().create(*args, **kwargs)
        # return all read articles on creation for performance gains: ED-2822
        return self.list(*args, **kwargs)


class TaskCompletedCreateRetrieveView(mixins.FilterBySSOIdMixin,
                                      ListCreateAPIView):
    serializer_class = serializers.TaskCompletedSerializer
