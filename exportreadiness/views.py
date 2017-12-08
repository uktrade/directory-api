from rest_framework.generics import (
    CreateAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)

from exportreadiness import mixins, models, serializers


class TriageResultCreateRetrieveView(
    mixins.GetObjectOr404FromSSOIdMixin, CreateAPIView, RetrieveAPIView,
    UpdateAPIView
):
    serializer_class = serializers.TriageResultSerializer


class ArticleReadCreateRetrieveView(mixins.FilterBySSOIdMixin,
                                    ListCreateAPIView):
    serializer_class = serializers.ArticleReadSerializer
    model = models.ArticleRead.objects

    def is_bulk_create(self):
        return isinstance(self.request.data, list)

    def get_serializer(self, *args, **kwargs):
        # allow bulk creating articles read for performance gains: ED-2822
        if self.is_bulk_create():
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)

    def create(self, *args, **kwargs):
        if not self.is_bulk_create():
            # if article already seen then do nothing
            queryset = self.model.filter(
                sso_id=self.request.user.id,
                article_uuid=self.request.data.get('article_uuid'),
            )
            if queryset.exists():
                return self.list(*args, **kwargs)
        super().create(*args, **kwargs)
        # return all read articles on creation for performance gains: ED-2822
        return self.list(*args, **kwargs)


class TaskCompletedCreateRetrieveView(mixins.FilterBySSOIdMixin,
                                      ListCreateAPIView):
    serializer_class = serializers.TaskCompletedSerializer
