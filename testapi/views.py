from directory_sso_api_client.client import DirectorySSOAPIClient
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
from testapi.serializers import UserSerializer

"""
GET /testapi/users/<email>/
{
  "sso_id": <sso-id>,
  "is_verified": True/False
}
"""


class UserAPIView(APIView):
    base_url=SSO_PROXY_API_CLIENT_BASE_URL
    sso_api_client = DirectorySSOAPIClient(
        base_url=base_url, api_key=SSO_PROXY_SIGNATURE_SECRET)

    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = []

    def dispatch(self, *args, **kwargs):
        if not settings.ENABLE_TEST_API:
            raise Http404()
        return super().dispatch(*args, **kwargs)

    def get(self, request: Request, email: str, format: str = None):
        sso_response = self.sso_api_client.get_user_by_email(email=email)
        if sso_response.status_code == status.HTTP_200_OK:
            serializer = self.serializer_class(sso_response.json())
            return Response(serializer.data)
        else:
            raise Http404()
