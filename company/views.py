import abc

from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework import generics, viewsets, views, status

from django.db.models import Case, Count, When, Value, BooleanField
from django.db.models import Q
from django.http import Http404

import company.serializers
from company import documents, filters, helpers, models, pagination, permissions, serializers
from core.permissions import IsAuthenticatedSSO
from supplier.helpers import validate_other_admins_connected_to_company


class CompanyNumberValidatorAPIView(generics.GenericAPIView):

    serializer_class = serializers.CompanyNumberValidatorSerializer
    permission_classes = []

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
        .filter(
            Q(is_published_find_a_supplier=True) |
            Q(is_published_investment_support_directory=True)
        )
        .annotate(supplier_case_studies_count=Count('supplier_case_studies'))
        .annotate(
            has_case_studies=Case(
               When(supplier_case_studies_count=0, then=Value(False)),
               default=Value(True),
               output_field=BooleanField())
        )
        .order_by('-has_case_studies', '-modified')
    )
    permission_classes = []
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
        Q(company__is_published_find_a_supplier=True) |
        Q(company__is_published_investment_support_directory=True)
    )
    lookup_field = 'pk'
    permission_classes = []
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


class RequestVerificationWithIdentificationView(views.APIView):

    def post(self, request, *args, **kwargs):
        helpers.send_request_identity_verification_message(self.request.user.supplier)
        return Response()


class AbstractSearchAPIView(abc.ABC, views.APIView):

    permission_classes = []
    serializer_class = serializers.SearchSerializer

    @property
    @abc.abstractmethod
    def elasticsearch_filter(self):
        return {}

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.GET)
        serializer.is_valid(raise_exception=True)
        params = {
            key: value for key, value in serializer.validated_data.items()
            if key in serializer.OPTIONAL_FILTERS
        }
        query = helpers.build_search_company_query(params)
        size = serializer.validated_data['size']
        search_object = (
            documents.CompanyDocument
            .search()
            .filter('term', **self.elasticsearch_filter)
            .query(query)
            .sort(
                {"_score": {"order": "desc"}},
                {"ordering_name": {"order": "asc"}},
            )
            .highlight_options(require_field_match=False)
            .highlight('summary', 'description')
            .extra(
                from_=(serializer.validated_data['page'] - 1) * size,
                size=size,
            )
        )
        return Response(data=search_object.execute().to_dict())


class FindASupplierSearchAPIView(AbstractSearchAPIView):
    elasticsearch_filter = {
        'is_published_find_a_supplier': True
    }


class InvestmentSupportDirectorySearchAPIView(AbstractSearchAPIView):
    elasticsearch_filter = {
        'is_published_investment_support_directory': True
    }


class CollaboratorInviteCreateView(generics.CreateAPIView):
    serializer_class = serializers.CollaboratorInviteSerializer
    permission_classes = [IsAuthenticatedSSO, permissions.IsCompanyAdmin]


class TransferOwnershipInviteCreateView(generics.CreateAPIView):
    serializer_class = serializers.OwnershipInviteSerializer
    permission_classes = [IsAuthenticatedSSO, permissions.IsCompanyAdmin]


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
    permission_classes = [IsAuthenticatedSSO, permissions.IsCompanyAdmin]

    def get_queryset(self):
        return self.request.user.supplier.company.suppliers.exclude(
            pk=self.request.user.supplier.pk
        )

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        sso_ids = serializer.validated_data['sso_ids']
        validate_other_admins_connected_to_company(company=self.request.user.supplier.company, sso_ids=sso_ids)
        self.get_queryset().filter(sso_id__in=sso_ids).update(company=None)
        return Response()


class CollaboratorRequestView(generics.CreateAPIView):
    serializer_class = serializers.CollaboratorRequestSerializer
    permission_classes = []

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        data = {'company_email': serializer.instance.company.email_address}
        return Response(data, status=201)



class CollaborationInviteViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CollaborationInviteSerializer
    permission_classes = [IsAuthenticatedSSO, permissions.IsCompanyAdmin]
    queryset = models.CollaborationInvite.objects.all()

    def perform_create(self, serializer):
        serializer.save(
            requestor=self.request.user.supplier.pk,
            company=self.request.user.supplier.company.pk,
        )


class AddCollaboratorView(CreateAPIView):
    serializer_class = company.serializers.AddCollaboratorSerializer
    permission_classes = []
