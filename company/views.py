from rest_framework.generics import RetrieveUpdateAPIView

from company.models import Company
from company.serializers import CompanySerializer


class CompanyRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
