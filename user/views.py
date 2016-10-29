import json

from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from user.serializers import UserSerializer, ConfirmCompanyEmailSerializer
from user.models import User


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    queryset = User.objects.all()
    lookup_field = 'sso_id'
    serializer_class = UserSerializer


class ConfirmCompanyEmailAPIView(APIView):

    http_method_names = ("post", )
    serializer_class = ConfirmCompanyEmailSerializer

    def post(self, request, *args, **kwargs):
        """Confirms enrolment by company_email verification"""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = User.objects.get(
                company_email_confirmation_code=serializer.data[
                    'confirmation_code'
                ]
            )
        except User.DoesNotExist:
            response_status_code = status.HTTP_400_BAD_REQUEST
            response_data = json.dumps({
                "status_code": response_status_code,
                "detail": "Invalid company email confirmation code"
            })
        else:
            user.company_email_confirmed = True
            user.save()

            response_status_code = status.HTTP_200_OK
            response_data = json.dumps({
                "status_code": response_status_code,
                "detail": "Company email confirmed"
            })

        return Response(
            data=response_data,
            status=response_status_code,
        )
