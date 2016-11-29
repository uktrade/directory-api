import json

from rest_framework import status
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.renderers import JSONRenderer
from rest_framework.authentication import BasicAuthentication
from rest_framework.permissions import IsAuthenticated

from user import models, serializers, gecko


class UserEmailValidatorAPIView(GenericAPIView):

    serializer_class = serializers.UserEmailValidatorSerializer

    def get(self, request, *args, **kwargs):
        validator = self.get_serializer(data=request.GET)
        validator.is_valid(raise_exception=True)
        return Response()


class UserMobileNumberValidatorAPIView(GenericAPIView):

    serializer_class = serializers.UserMobileNumberValidatorSerializer

    def get(self, request, *args, **kwargs):
        validator = self.get_serializer(data=request.GET)
        validator.is_valid(raise_exception=True)
        return Response()


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    queryset = models.User.objects.all()
    lookup_field = 'sso_id'
    serializer_class = serializers.UserSerializer


class GeckoTotalRegisteredUsersView(APIView):

    permission_classes = (IsAuthenticated, )
    authentication_classes = (BasicAuthentication, )
    renderer_classes = (JSONRenderer, )
    http_method_names = ("get", )

    def get(self, request, format=None):
        return Response(gecko.total_registered_users())


class ConfirmCompanyEmailAPIView(APIView):

    http_method_names = ("post", )
    serializer_class = serializers.ConfirmCompanyEmailSerializer

    def post(self, request, *args, **kwargs):
        """Confirms enrolment by company_email verification"""

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            user = models.User.objects.get(
                company_email_confirmation_code=serializer.data[
                    'confirmation_code'
                ]
            )
        except models.User.DoesNotExist:
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
