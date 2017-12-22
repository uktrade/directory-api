from rest_framework.fields import empty
from rest_framework.generics import get_object_or_404

from django.http import QueryDict


class InjectSSOIDMixin:

    def run_validation(self, data=empty):
        if data:
            if isinstance(data, QueryDict):
                data = data.dict()
            data['sso_id'] = self.context['request'].user.id
        return super().run_validation(data)


class GetObjectOr404FromSSOIdMixin:
    def get_object(self):
        model_class = self.serializer_class.Meta.model
        return get_object_or_404(
            model_class.objects.all(),
            sso_id=self.request.user.id
        )


class FilterBySSOIdMixin:

    def get_queryset(self):
        model_class = self.serializer_class.Meta.model
        return model_class.objects.filter(
            sso_id=self.request.user.id
        )
