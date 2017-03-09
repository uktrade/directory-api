from notifications import models, serializers

from django.db.utils import IntegrityError

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response


class AnonymousUnsubscribeCreateAPIView(CreateAPIView):

    model = models.AnonymousUnsubscribe
    serializer_class = serializers.AnonymousUnsubscribeSerializer

    def create(self, *args, **kwargs):
        try:
            return super().create(*args, **kwargs)
        # if email has already unsubscribed integrity error happens
        except IntegrityError:
            return Response()
