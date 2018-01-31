from directory_sso_api_client.testapiclient import DirectoryTestAPIClient
from django.http import Http404
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from api import settings
from api.settings import (
    SSO_PROXY_API_CLIENT_BASE_URL,
    SSO_PROXY_SIGNATURE_SECRET,
)
from testapi.permissions import IsAuthenticatedTestAPI
from testapi.serializers import UserSerializer


class UserAPIView(APIView):
    base_url=SSO_PROXY_API_CLIENT_BASE_URL
    sso_api_client = DirectoryTestAPIClient(
        base_url=base_url, api_key=SSO_PROXY_SIGNATURE_SECRET)

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticatedTestAPI]
    http_method_names = ("get", )

    def dispatch(self, *args, **kwargs):
        if not settings.TEST_API_ENABLE:
            raise Http404()
        return super().dispatch(*args, **kwargs)

    def get(self, request: Request, email: str, format: str = None):
        token = request.GET.get('token')
        sso_response = self.sso_api_client.get_user_by_email(email=email, token=token)
        if sso_response.status_code == status.HTTP_200_OK:
            serializer = self.serializer_class(sso_response.json())
            return Response(serializer.data)
        else:
            raise Http404()
