from directory_sso_api_client.user import UserAPIClient
from rest_framework.response import Response
from rest_framework.views import APIView

from testapi.serializers import UserSerializer

"""
GET /testapi/users/<email>/
{
  "sso_id": <sso-id>,
  "email_verification_link": "<verification-link>",
  "is_verified": True/False
}
"""


class UserAPIView(APIView):
    client = UserAPIClient(
        base_url='http://sso.trade.great:8003', api_key='debug'
    )

    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, email: str, format: str = None):
        response = self.client.get_user_by_email(email=email)
        response_data = {
            "sso_id": response.status_code,
            "email_verification_link": "verification link",
            "is_verified": True
        }
        serializer = self.serializer_class(response_data)
        return Response(serializer.data)
