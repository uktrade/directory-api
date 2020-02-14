from rest_framework import generics
from rest_framework import status
from rest_framework.response import Response

from core.permissions import IsAuthenticatedSSO
from personalisation import models, serializers


class UserLocationCreateAPIView(generics.ListCreateAPIView):
    serializer_class = serializers.UserLocationSerializer
    permission_classes = [IsAuthenticatedSSO]
    queryset = models.UserLocation.objects.all()

    def perform_create(self, serializer):
        serializer.validated_data['sso_id'] = self.request.user.id
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # no need to save user's city if we already know about it
        queryset = self.get_queryset().filter(
            region=serializer.validated_data['region'],
            country=serializer.validated_data['country'],
            city=serializer.validated_data['city'],
            sso_id=self.request.user.id,
        )
        if not queryset.exists():
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        else:
            return Response(serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        return models.UserLocation.objects.filter(sso_id=self.request.user.id)
