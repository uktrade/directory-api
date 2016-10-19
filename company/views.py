from rest_framework.generics import RetrieveUpdateAPIView

from company.serializers import CompanySerializer
from company.models import Company


class CompanyRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    queryset = Company.objects.all()
    serializer_class = CompanySerializer
