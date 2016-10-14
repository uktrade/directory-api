from rest_framework.generics import RetrieveUpdateAPIView

from company.serializers import CompanySerializer
from company.models import Company


class CompanyRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    model = Company
    serializer_class = CompanySerializer

    def get_queryset(self):
        return self.model.objects.all()
