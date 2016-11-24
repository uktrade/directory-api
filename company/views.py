from rest_framework.generics import (
    GenericAPIView, RetrieveUpdateAPIView, get_object_or_404
)
from rest_framework.response import Response
from rest_framework import viewsets

from company import models, serializers


class CompanyNumberValidatorAPIView(GenericAPIView):

    serializer_class = serializers.CompanyNumberValidatorSerializer

    def get(self, request, *args, **kwargs):
        validator = self.get_serializer(data=request.GET)
        validator.is_valid(raise_exception=True)
        return Response()


class CompanyRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    serializer_class = serializers.CompanySerializer

    def get_object(self):
        return get_object_or_404(
            models.Company, users__sso_id=self.kwargs['sso_id']
        )


class CompanyCaseStudyViewSet(viewsets.ModelViewSet):

    serializer_class = serializers.CompanyCaseStudySerializer
    queryset = models.CompanyCaseStudy.objects.all()

    def dispatch(self, *args, **kwargs):
        self.company = get_object_or_404(
            models.Company, users__sso_id=kwargs['sso_id']
        )
        return super().dispatch(*args, **kwargs)

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['company'] = self.company.pk
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(company=self.company)
