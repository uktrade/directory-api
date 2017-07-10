from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from django.db.utils import IntegrityError

from api.signature import SignatureCheckPermission
from notifications import models, notifications, serializers


class AnonymousUnsubscribeCreateAPIView(CreateAPIView):

    model = models.AnonymousUnsubscribe
    serializer_class = serializers.AnonymousUnsubscribeSerializer
    permission_classes = [SignatureCheckPermission]

    def create(self, *args, **kwargs):
        try:
            return super().create(*args, **kwargs)
        # if email has already unsubscribed integrity error happens
        except IntegrityError:
            return Response()

    def perform_create(self, serializer):
        instance = serializer.save()
        notifications.anonymous_unsubscribed(
            recipient_email=instance.email
        )
