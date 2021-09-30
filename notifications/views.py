from django.db.utils import IntegrityError
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

from notifications import models, notifications, serializers, tokens


class AnonymousUnsubscribeCreateAPIView(CreateAPIView):

    model = models.AnonymousUnsubscribe
    serializer_class = serializers.AnonymousUnsubscribeSerializer
    permission_classes = []

    def create(self, *args, **kwargs):
        try:
            self.request.data._mutable = True
            self.request.data['email'] = self.get_email()
            self.request.data._mutable = False
            return super().create(*args, **kwargs)
        # if email has already unsubscribed integrity error happens
        except IntegrityError:
            return Response()

    def perform_create(self, serializer):
        instance = serializer.save()
        notifications.anonymous_unsubscribed(recipient_email=instance.email)

    def get_email(self):
        email = self.request.data.get('email')

        if email is not None:
            return email

        uidb64 = self.request.data.get('uidb64')
        token = self.request.data.get('token')

        if uidb64 is None or token is None:
            return None

        try:
            uid = force_text(urlsafe_base64_decode(uidb64))
            notification = models.AnonymousEmailNotification.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, models.AnonymousEmailNotification.DoesNotExist):
            notification = None

        if notification is not None and tokens.anonymous_unsubscribe_token.check_token(notification, token):
            return notification.email
