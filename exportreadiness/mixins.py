from rest_framework.generics import get_object_or_404


class InjectSSOIDCreateMixin:

    def create(self, validated_data):
        sso_id = self.context['request'].user.id
        validated_data['sso_id'] = sso_id
        return super().create(validated_data)


class GetObjectOr404FromSSOIdMixin:
    def get_object(self):
        model_class = self.serializer_class.Meta.model
        return get_object_or_404(
            model_class.objects.all(),
            sso_id=self.request.user.id
        )
