import abc

from directory_constants import user_roles
from django.conf import settings
from django.db.models import BooleanField, Case, Count, Q, Value, When
from django.http import Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import generics, status, views, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

from company import documents, filters, gecko, helpers, models, pagination, permissions, serializers
from core import authentication
from core.permissions import IsAuthenticatedSSO
from core.views import CSVDumpAPIView
from notifications import notifications


class CompanyNumberValidatorAPIView(generics.GenericAPIView):

    serializer_class = serializers.CompanyNumberValidatorSerializer
    permission_classes = []

    def get(self, request, *args, **kwargs):
        validator = self.get_serializer(data=request.GET)
        validator.is_valid(raise_exception=True)
        return Response()


class CompanyDestroyAPIView(generics.DestroyAPIView):
    authentication_classes = [
        authentication.Oauth2AuthenticationSSO,
    ]
    permission_classes = [permissions.ValidateDeleteRequest]

    @csrf_exempt
    def delete(self, request, *args, **kwargs):
        """
        delete endpoint will take sso_id (user_id) as kwargs to delete company
           > IF user is only user for associated company
             then we delete user and company
           > IF multiple users associated for a company and requested user is admin
             then we re-assign admin role to other users
             and delete user only, no company get deleted in this case.
        """
        sso_id = kwargs['sso_id']
        try:
            request_user = models.CompanyUser.objects.get(sso_id=sso_id)
        except models.CompanyUser.DoesNotExist:
            return HttpResponse(status=204)

        companies = models.Company.objects.filter(company_users__sso_id=sso_id)
        if not companies:
            request_user.delete()
            # nothing else to do
            return HttpResponse(status=204)

        for company in companies:
            # check if company has other users
            company_users = models.CompanyUser.objects.filter(company=company)
            number_of_company_users = company_users.count()
            # remove user
            if number_of_company_users == 1:
                request_user.delete()
                company.delete()
            elif number_of_company_users > 1:
                if request_user.role == user_roles.ADMIN:
                    other_users = company_users.filter(~Q(sso_id=sso_id))
                    other_users.update(role=user_roles.ADMIN)
                request_user.delete()

        return HttpResponse(status=204)


class CompanyRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.CompanySerializer

    def get_object(self):
        if self.request.user.company:
            return self.request.user.company
        raise Http404()

    def partial_update(self, request, *args, **kwargs):
        # create the objects if they do not yet exist, allowing for piecemeal company creation
        company, _ = models.Company.objects.get_or_create(company_users__sso_id=self.request.user.id)
        models.CompanyUser.objects.update_or_create(
            sso_id=self.request.user.id, defaults={'company': company, 'company_email': self.request.user.email}
        )

        # invalidate the cached_property
        try:
            del self.request.user.company_user
        except AttributeError:
            pass
        return super().partial_update(request, *args, **kwargs)


class CompanyPublicProfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CompanySerializer
    queryset = (
        models.Company.objects.filter(
            Q(is_published_find_a_supplier=True) | Q(is_published_investment_support_directory=True)
        )
        .annotate(supplier_case_studies_count=Count('supplier_case_studies'))
        .annotate(
            has_case_studies=Case(
                When(supplier_case_studies_count=0, then=Value(False)), default=Value(True), output_field=BooleanField()
            )
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
        return self.queryset.filter(company_id=self.request.user.company.id)


class PublicCaseStudyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = models.CompanyCaseStudy.objects.filter(
        Q(company__is_published_find_a_supplier=True) | Q(company__is_published_investment_support_directory=True)
    )
    lookup_field = 'pk'
    permission_classes = []
    serializer_class = serializers.CompanyCaseStudyWithCompanySerializer


class VerifyCompanyWithCodeAPIView(views.APIView):
    """
    Confirms CompanyUser's relationship with Company by providing proof of
    access to the Company's physical address.

    """

    http_method_names = ("post",)
    serializer_class = serializers.VerifyCompanyWithCodeSerializer
    renderer_classes = (JSONRenderer,)

    def post(self, request, *args, **kwargs):

        company = self.request.user.company
        serializer = self.serializer_class(data=request.data, context={'expected_code': company.verification_code})
        serializer.is_valid(raise_exception=True)

        company.verified_with_code = True
        company.save()

        return Response(
            data={"status_code": status.HTTP_200_OK, "detail": "Company verified with code"},
            status=status.HTTP_200_OK,
        )


class VerifyCompanyWithCompaniesHouseView(views.APIView):
    """
    Confirms CompanyUser's relationship with Company by providing proof of
    being able to login to the Company's Companies House profile.

    """

    serializer_class = serializers.VerifyCompanyWithCompaniesHouseSerializer

    def post(self, request, *args, **kwargs):
        company = self.request.user.company
        serializer = self.serializer_class(data=request.data, context={'company_number': company.number})
        serializer.is_valid(raise_exception=True)
        company.verified_with_companies_house_oauth2 = True
        company.save()

        return Response()


class RequestVerificationWithIdentificationView(views.APIView):
    def post(self, request, *args, **kwargs):
        helpers.send_request_identity_verification_message(self.request.user.company_user)
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
        params = {key: value for key, value in serializer.validated_data.items() if key in serializer.OPTIONAL_FILTERS}
        query = helpers.build_search_company_query(params)
        size = serializer.validated_data['size']
        search_object = (
            documents.CompanyDocument.search()
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
    elasticsearch_filter = {'is_published_find_a_supplier': True}


class InvestmentSupportDirectorySearchAPIView(AbstractSearchAPIView):
    elasticsearch_filter = {'is_published_investment_support_directory': True}


class RemoveCollaboratorsView(views.APIView):
    serializer_class = serializers.RemoveCollaboratorsSerializer
    permission_classes = [IsAuthenticatedSSO, permissions.IsCompanyAdmin]

    def get_queryset(self):
        return self.request.user.company.company_users.exclude(pk=self.request.user.company_user.pk)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        sso_ids = serializer.validated_data['sso_ids']
        helpers.validate_other_admins_connected_to_company(company=self.request.user.company, sso_ids=sso_ids)
        self.get_queryset().filter(sso_id__in=sso_ids).update(company=None)
        return Response()


class CollaborationRequestView(viewsets.ModelViewSet):
    serializer_class = serializers.CollaborationRequestSerializer
    queryset = models.CollaborationRequest.objects.all()
    lookup_field = 'uuid'

    def get_permissions(self):
        if self.action == 'partial_update':
            permission_classes = [IsAuthenticatedSSO, permissions.IsCompanyAdmin]
        else:
            permission_classes = [IsAuthenticatedSSO]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        serializer.save(
            requestor=self.request.user.company_user,
            name=self.request.user.company_user.name,
        )

    def get_queryset(self):
        return self.queryset.filter(requestor__company__id=self.request.user.company.id)


class CollaborationInviteViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CollaborationInviteSerializer
    queryset = models.CollaborationInvite.objects.all()
    lookup_field = 'uuid'

    def get_permissions(self):
        if self.action == 'retrieve':
            permission_classes = []
        elif self.action == 'partial_update':
            permission_classes = [IsAuthenticatedSSO]
        else:
            permission_classes = [IsAuthenticatedSSO, permissions.IsCompanyAdmin]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action in ['retrieve', 'partial_update']:
            return self.queryset
        return self.queryset.filter(company_id=self.request.user.company.id)

    def perform_create(self, serializer):
        serializer.save(
            company_user=self.request.user.company_user,
            company=self.request.user.company,
        )


class AddCollaboratorView(generics.CreateAPIView):
    serializer_class = serializers.AddCollaboratorSerializer
    permission_classes = [IsAuthenticatedSSO]


class ChangeCollaboratorRoleView(generics.UpdateAPIView):
    serializer_class = serializers.ChangeCollaboratorRoleSerializer
    permission_classes = [IsAuthenticatedSSO, permissions.IsCompanyAdmin]
    lookup_field = 'sso_id'

    def get_queryset(self):
        return models.CompanyUser.objects.filter(company_id=self.request.user.company.id)


class CompanyUserRetrieveAPIView(views.APIView):
    serializer_class = serializers.ExternalCompanyUserSerializer
    authentication_classes = [
        authentication.Oauth2AuthenticationSSO,
        authentication.SessionAuthenticationSSO,
    ]

    def get(self, request):
        if not self.request.user.company_user:
            raise Http404()
        serializer = self.serializer_class(request.user.company_user)
        return Response(serializer.data)


class CompanyUserSSOListAPIView(generics.ListAPIView):
    queryset = models.CompanyUser.objects.all()
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        # normally DRF loops over the queryset and calls the serializer on each
        # supplier- which is much less performant than calling `values_list`
        sso_ids = self.queryset.values_list('sso_id', flat=True)
        return Response(data=sso_ids)


class CompanyUserRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.CompanyUserSerializer

    def get_object(self):
        if not self.request.user.company_user:
            raise Http404()
        return self.request.user.company_user


class GeckoTotalRegisteredCompanyUser(views.APIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (authentication.GeckoBasicAuthentication,)
    renderer_classes = (JSONRenderer,)
    http_method_names = ("get",)

    def get(self, request, format=None):
        return Response(gecko.total_registered_company_users())


class CompanyUserUnsubscribeAPIView(views.APIView):

    http_method_names = ("post",)

    def post(self, request, *args, **kwargs):
        """Unsubscribes supplier from notifications"""
        company_user = self.request.user.company_user
        company_user.unsubscribed = True
        company_user.save()
        notifications.company_user_unsubscribed(company_user=company_user)
        return Response(
            data={"status_code": status.HTTP_200_OK, "detail": "CompanyUser unsubscribed"},
            status=status.HTTP_200_OK,
        )


class CompanyCollboratorsListView(generics.ListAPIView):
    permission_classes = [IsAuthenticatedSSO]
    serializer_class = serializers.CompanyUserSerializer

    def get_queryset(self):
        return models.CompanyUser.objects.filter(company_id=self.request.user.company.id)


class CollaboratorDisconnectView(views.APIView):
    permission_classes = [IsAuthenticatedSSO]

    def get_object(self):
        return self.request.user.company_user

    def post(self, request, *args, **kwargs):
        supplier = self.get_object()
        helpers.validate_other_admins_connected_to_company(company=supplier.company, sso_ids=[supplier.sso_id])
        supplier.company = None
        supplier.role = user_roles.MEMBER
        supplier.save()
        return Response()


class CompanyUserSSORetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = serializers.CompanyUserSerializer
    queryset = models.CompanyUser.objects.all()
    permission_classes = []
    lookup_url_kwarg = 'sso_id'
    lookup_field = 'sso_id'


if settings.STORAGE_CLASS_NAME == 'default':
    # this view only works if s3 is in use (s3 is default. in local dev local storage is used)
    class CompanyUserCSVDownloadAPIView(CSVDumpAPIView):
        bucket = settings.AWS_STORAGE_BUCKET_NAME_DATA_SCIENCE
        key = settings.SUPPLIERS_CSV_FILE_NAME
        filename = settings.SUPPLIERS_CSV_FILE_NAME
