from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import APIView

from company.models import Company
from company.serializers import CompanySerializer


class CompanyNumberValidatorAPIView(APIView):

    def get(self, request, *args, **kwargs):
        if 'number' not in request.GET:
            raise ValidationError({'number': ['This field is required']})
        if Company.objects.filter(number=request.GET['number']).exists():
            raise ValidationError({'number': ['Already registered']})
        return Response()


class CompanyRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
