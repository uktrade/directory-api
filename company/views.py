from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import generics, viewsets, views, status

from company import filters, models, pagination, permissions, serializers


class CompanyNumberValidatorAPIView(generics.GenericAPIView):

    serializer_class = serializers.CompanyNumberValidatorSerializer

    def get(self, request, *args, **kwargs):
        validator = self.get_serializer(data=request.GET)
        validator.is_valid(raise_exception=True)
        return Response()


class CompanyRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):

    serializer_class = serializers.CompanySerializer

    def get_object(self):
        return generics.get_object_or_404(
            models.Company, suppliers__sso_id=self.kwargs['sso_id']
        )


class CompanyPublicProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CompanySerializer
    queryset = models.Company.objects.filter(is_published=True)
    pagination_class = pagination.CompanyPublicProfile
    filter_class = filters.CompanyPublicProfileFilter
    lookup_url_kwarg = 'companies_house_number'
    lookup_field = 'number'


class CompanyCaseStudyViewSet(viewsets.ModelViewSet):

    read_serializer_class = serializers.CompanyCaseStudyWithCompanySerializer
    write_serializer_class = serializers.CompanyCaseStudySerializer
    queryset = models.CompanyCaseStudy.objects.all()
    permission_classes = [permissions.IsCaseStudyOwnerOrReadOnly]

    def get_serializer_class(self):
        # on read use nested serializer (to also expose company), on write use
        # flat serializer (so request can refer to existing company pk).
        if self.request.method == 'GET':
            return self.read_serializer_class
        return self.write_serializer_class

    def get_serializer(self, *args, **kwargs):
        if self.request.method == 'POST':
            # on case study create, get the company using the user's sso id.
            company = generics.get_object_or_404(
                models.Company, suppliers__sso_id=self.request.META['sso_id']
            )
            kwargs['data']['company'] = company.pk
        return super().get_serializer(*args, **kwargs)


class VerifyCompanyWithCodeAPIView(views.APIView):

    http_method_names = ("post", )
    serializer_class = serializers.VerifyCompanyWithCodeSerializer
    renderer_classes = (JSONRenderer, )

    def dispatch(self, *args, **kwargs):
        self.company = generics.get_object_or_404(
            models.Company, suppliers__sso_id=kwargs['sso_id']
        )
        return super().dispatch(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Confirms enrolment by company_email verification"""
        serializer = self.serializer_class(
            data=request.data,
            context={'expected_code': self.company.verification_code}
        )
        serializer.is_valid(raise_exception=True)

        self.company.verified_with_code = True
        self.company.save()

        return Response(
            data={
                "status_code": status.HTTP_200_OK,
                "detail": "Company verified with code"
            },
            status=status.HTTP_200_OK,
        )
