from rest_framework.response import Response
from rest_framework.views import APIView

from internal.serializers import UserSerializer

"""
GET /internal/user/<email>/
{
  "sso_id": <sso-id>,
  "email_verification_link": "<verification-link>",
  "is_verified": True/False
}
"""

class UserAPIView(APIView):

    serializer_class = UserSerializer
    authentication_classes = []
    permission_classes = []

    def get(self, request, email: str, format: str = None):
        response_data = {
            "sso_id": 1,
            "email_verification_link": "verification link",
            "is_verified": True
        }
        serializer = self.serializer_class(response_data)
        return Response(serializer.data)
