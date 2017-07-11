from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import generics, viewsets, views, status

from django.db.models import Case, Count, When, Value, BooleanField

from api.signature import SignatureCheckPermission
from company import filters, models, pagination, search, serializers


class CompanyNumberValidatorAPIView(generics.GenericAPIView):

    serializer_class = serializers.CompanyNumberValidatorSerializer
    permission_classes = [SignatureCheckPermission]

    def get(self, request, *args, **kwargs):
        validator = self.get_serializer(data=request.GET)
        validator.is_valid(raise_exception=True)
        return Response()


class CompanyRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.CompanySerializer

    def get_object(self):
        return self.request.user.supplier.company


class CompanyPublicProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CompanySerializer
    queryset = (
        models.Company.objects
        .filter(is_published=True)
        .annotate(supplier_case_studies_count=Count('supplier_case_studies'))
        .annotate(
            has_case_studies=Case(
               When(supplier_case_studies_count=0, then=Value(False)),
               default=Value(True),
               output_field=BooleanField())
        )
        .order_by('-has_case_studies', '-modified')
    )
    permission_classes = [SignatureCheckPermission]
    pagination_class = pagination.CompanyPublicProfile
    filter_class = filters.CompanyPublicProfileFilter
    lookup_url_kwarg = 'companies_house_number'
    lookup_field = 'number'


class CompanyCaseStudyViewSet(viewsets.ModelViewSet):

    read_serializer_class = serializers.CompanyCaseStudyWithCompanySerializer
    queryset = models.CompanyCaseStudy.objects.all()
    write_serializer_class = serializers.CompanyCaseStudySerializer

    def get_serializer_class(self):
        # on read use nested serializer (to also expose company), on write use
        # flat serializer (so request can refer to existing company pk).
        if self.request.method == 'GET':
            return self.read_serializer_class

        return self.write_serializer_class

    def get_serializer(self, *args, **kwargs):
        if 'data' in kwargs:
            kwargs['data']['company'] = self.request.user.supplier.company_id
        return super().get_serializer(*args, **kwargs)

    def get_queryset(self):
        return self.queryset.filter(
            company_id=self.request.user.supplier.company_id
        )


class PublicCaseStudyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.CompanyCaseStudy.objects.filter(
        company__is_published=True
    )
    lookup_field = 'pk'
    permission_classes = [SignatureCheckPermission]
    serializer_class = serializers.CompanyCaseStudyWithCompanySerializer


class VerifyCompanyWithCodeAPIView(views.APIView):

    http_method_names = ("post", )
    serializer_class = serializers.VerifyCompanyWithCodeSerializer
    renderer_classes = (JSONRenderer, )

    def post(self, request, *args, **kwargs):
        """Confirms enrolment by company_email verification"""
        company = self.request.user.supplier.company
        serializer = self.serializer_class(
            data=request.data,
            context={'expected_code': company.verification_code}
        )
        serializer.is_valid(raise_exception=True)

        company.verified_with_code = True
        company.save()

        return Response(
            data={
                "status_code": status.HTTP_200_OK,
                "detail": "Company verified with code"
            },
            status=status.HTTP_200_OK,
        )


class CompanySearchAPIView(views.APIView):

    http_method_names = ("get", )
    # `serializer_class` is used for deserializing the search query,
    # but not for serializing the search results.
    serializer_class = serializers.CompanySearchSerializer
    permission_classes = [SignatureCheckPermission]

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.GET)
        serializer.is_valid(raise_exception=True)
        search_results = self.get_search_results(
            term=serializer.data['term'],
            page=serializer.data['page'],
            size=serializer.data['size'],
        )
        return Response(
            data=search_results,
            status=status.HTTP_200_OK,
        )

    @staticmethod
    def get_search_results(term, page, size):
        """Search companies by term

        Wildcard search of companies by provided term. The position of
        companies that have only one sector is increased.

        Arguments:
            term {str} -- Search term to match on
            page {int} -- Page number to query
            size {int} -- Number of results per page

        Returns:
            dict -- Companies that match the term

        """

        start = (page - 1) * size
        end = start + size
        search_object = search.CompanyDocType.search()
        response = search_object.query('match', _all=term)[start:end].execute()
        return response.to_dict()
