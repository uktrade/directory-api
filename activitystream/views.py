from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


class ActivityStreamViewSet(ViewSet):
    permission_classes = (AllowAny,)

    def list(self, request):
        return Response({})
