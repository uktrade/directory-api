from rest_framework.generics import RetrieveUpdateAPIView

from company.serializers import CompanySerializer
from company.models import Company


class CompanyRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    model = Company
    queryset = model.objects
    serializer_class = CompanySerializer
