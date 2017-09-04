from rest_framework import generics

from .serializers import OwnershipInviteSerializer


class TransferOwnershipView(generics.CreateAPIView):
    serializer_class = OwnershipInviteSerializer

