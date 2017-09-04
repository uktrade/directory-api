from rest_framework import generics

from .serializers import OwnershipInviteSerializer


class TransferOwnershipInviteCreateView(generics.CreateAPIView):
    serializer_class = OwnershipInviteSerializer
