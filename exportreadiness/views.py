from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.serializers import ValidationError

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

    def handle_exception(self, exc):
        if isinstance(exc, ValidationError):
            # ignore because it will be "already seen article" - ignoring it
            # means clients don't need to check if the user has already seen
            # the article before calling the API for performance gains: ED-2822
            return self.list(self.request, *self.args, **self.kwargs)
        return super().handle_exception(exc)


class TaskCompletedCreateRetrieveView(mixins.FilterBySSOIdMixin,
                                      ListCreateAPIView):
    serializer_class = serializers.TaskCompletedSerializer
