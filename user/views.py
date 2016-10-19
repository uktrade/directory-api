import json

from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response

from user.serializers import UserSerializer
from user.models import User


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer


class ConfirmCompanyEmailAPIView(GenericAPIView):

    http_method_names = ("get", )

    def get(self, request, *args, **kwargs):
        """Confirms enrolment by company_email verification"""

        company_email_confirmed = request.user.confirm_company_email(
            confirmation_code=request.GET.get('confirmation_code')
        )

        if company_email_confirmed:
            response_status_code = status.HTTP_200_OK
            response_data = json.dumps({
                "status_code": response_status_code,
                "detail": "Email confirmed"
            })
        else:
            response_status_code = status.HTTP_400_BAD_REQUEST
            response_data = json.dumps({
                "status_code": response_status_code,
                "detail": "Invalid confirmation code"
            })

        return Response(
            data=response_data,
            status=response_status_code,
        )
