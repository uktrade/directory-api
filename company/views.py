import abc

from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import generics, viewsets, views, status

from django.db.models import Case, Count, When, Value, BooleanField
from django.http import Http404

from api.signature import SignatureCheckPermission
from company import filters, models, pagination, search, serializers
from core.permissions import IsAuthenticatedSSO
from supplier.permissions import IsCompanyProfileOwner
from supplier.models import Supplier

from elasticsearch_dsl import query


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
        if self.request.user.supplier and self.request.user.supplier.company:
            return self.request.user.supplier.company
        raise Http404()


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
    """
    Confirms Supplier's relationship with Company by providing proof of
    access to the Company's physical address.

    """

    http_method_names = ("post", )
    serializer_class = serializers.VerifyCompanyWithCodeSerializer
    renderer_classes = (JSONRenderer, )

    def post(self, request, *args, **kwargs):

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


class VerifyCompanyWithCompaniesHouseView(views.APIView):
    """
    Confirms Supplier's relationship with Company by providing proof of
    being able to login to the Company's Companies House profile.

    """

    serializer_class = serializers.VerifyCompanyWithCompaniesHouseSerializer

    def post(self, request, *args, **kwargs):
        company = self.request.user.supplier.company
        serializer = self.serializer_class(
            data=request.data,
            context={'company_number': company.number}
        )
        serializer.is_valid(raise_exception=True)
        company.verified_with_companies_house_oauth2 = True
        company.save()

        return Response()


class VerifyCompanyWithGovUKVerifyView(views.APIView):
    """
    Confirms Supplier's relationship with Company by their name and date of
    birth being matched against a company officer.

    """

    queryset = Supplier.objects.all()
    serializer_class = serializers.VerifyCompanyWithGovUKVerifySerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            self.request.user.supplier, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.validated_data)


class SearchBaseView(abc.ABC, views.APIView):
    http_method_names = ("get", )
    # `serializer_class` is used for deserializing the search query,
    # but not for serializing the search results.
    serializer_class = serializers.SearchSerializer
    permission_classes = [SignatureCheckPermission]

    sector_field_name = abc.abstractproperty()
    apply_highlighting = abc.abstractproperty()

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.GET)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        search_results = self.get_search_results(
            term=validated_data.get('term'),
            page=validated_data['page'],
            size=validated_data['size'],
            sectors=validated_data.get('sectors'),
            campaign_tag=validated_data.get('campaign_tag'),
            is_showcase_company=validated_data.get('is_showcase_company'),
        )
        return Response(
            data=search_results,
            status=status.HTTP_200_OK,
        )

    def get_search_results(
        self, term, page, size, sectors, campaign_tag, is_showcase_company=None
    ):
        """Search by term and filter by sector.

        Arguments:
            term {str}   -- Search term to match on
            page {int}   -- Page number to query
            size {int}   -- Number of results per page
            sectors {str[]} -- Filter companies by these sectors

        Returns:
            dict -- Companies that match the term

        """

        search_object = self.create_search_object(
            term=term,
            sectors=sectors,
            campaign_tag=campaign_tag,
            is_showcase_company=is_showcase_company,
        )
        search_object = self.apply_highlighting(search_object)
        search_object = self.apply_pagination(search_object, page, size)
        return search_object.execute().to_dict()

    def create_query_object(
        self, term, sectors, campaign_tag, is_showcase_company=None
    ):
        should_filters = []
        must_filters = []
        if sectors:
            for sector in sectors:
                params = {self.sector_field_name: sector}
                should_filters.append(query.Match(**params))
        if campaign_tag:
            should_filters.append(
                query.MatchPhrase(campaign_tag=campaign_tag)
            )
        if is_showcase_company is True:
            must_filters.append(query.Term(is_showcase_company=True))
        if term:
            must_filters.append(query.MatchPhrase(_all=term))
        return query.Bool(
            must=must_filters,
            should=should_filters,
            minimum_should_match=1 if len(should_filters) else 0,
        )

    @staticmethod
    def apply_pagination(search_object, page, size):
        start = (page - 1) * size
        end = start + size
        return search_object[start:end]


class CaseStudySearchAPIView(SearchBaseView):
    sector_field_name = 'sector'

    def create_search_object(
        self, term, sectors, campaign_tag, is_showcase_company
    ):
        query_object = self.create_query_object(
            term=term, sectors=sectors, campaign_tag=campaign_tag
        )
        return search.CaseStudyDocType.search().query(query_object)

    @staticmethod
    def apply_highlighting(search_object):
        return search_object


class CompanySearchAPIView(SearchBaseView):
    sector_field_name = 'sectors'

    def create_search_object(
        self, term, sectors, campaign_tag, is_showcase_company
    ):
        no_description = query.Term(has_description=False)
        has_description = query.Term(has_description=True)
        no_case_study = query.Term(case_study_count=0)
        one_case_study = query.Term(case_study_count=1)
        multiple_case_studies = query.Range(case_study_count={'gt': 1})

        query_object = self.create_query_object(
            term=term,
            sectors=sectors,
            campaign_tag=campaign_tag,
            is_showcase_company=is_showcase_company,
        )
        return search.CompanyDocType.search().query(
            'function_score',
            query=query_object,
            functions=[
                query.SF({
                  'weight': 5,
                  'filter': multiple_case_studies + has_description,
                }),
                query.SF({
                  'weight': 4,
                  'filter': multiple_case_studies + no_description,
                }),
                query.SF({
                  'weight': 3,
                  'filter': one_case_study + has_description,
                }),
                query.SF({
                  'weight': 2,
                  'filter': one_case_study + no_description,
                }),
                query.SF({
                  'weight': 1,
                  'filter': no_case_study + has_description,
                }),
            ],
            boost_mode='sum',
        )

    @staticmethod
    def apply_highlighting(search_object):
        return search_object.highlight_options(
            require_field_match=False,
        ).highlight('summary', 'description')


class CollaboratorInviteCreateView(generics.CreateAPIView):
    serializer_class = serializers.CollaboratorInviteSerializer
    permission_classes = [
        SignatureCheckPermission,
        IsAuthenticatedSSO,
        IsCompanyProfileOwner,
    ]


class TransferOwnershipInviteCreateView(generics.CreateAPIView):
    serializer_class = serializers.OwnershipInviteSerializer
    permission_classes = [
        SignatureCheckPermission,
        IsAuthenticatedSSO,
        IsCompanyProfileOwner,
    ]


class CollaboratorInviteRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.CollaboratorInviteSerializer
    queryset = models.CollaboratorInvite.objects.all()
    lookup_field = 'uuid'


class TransferOwnershipInviteRetrieveUpdateAPIView(
    generics.RetrieveUpdateAPIView
):
    serializer_class = serializers.OwnershipInviteSerializer
    queryset = models.OwnershipInvite.objects.all()
    lookup_field = 'uuid'


class RemoveCollaboratorsView(views.APIView):
    serializer_class = serializers.RemoveCollaboratorsSerializer
    permission_classes = [
        SignatureCheckPermission,
        IsAuthenticatedSSO,
        IsCompanyProfileOwner,
    ]

    def get_queryset(self):
        return self.request.user.supplier.company.suppliers.exclude(
            pk=self.request.user.supplier.pk
        )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        sso_ids = serializer.validated_data['sso_ids']
        self.get_queryset().filter(sso_id__in=sso_ids).update(company=None)
        return Response()
