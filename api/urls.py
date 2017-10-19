import django
from django.conf.urls import url, include
from django.contrib import admin

from api.views import HealthCheckAPIView
from company.views import (
    CompanyCaseStudyViewSet,
    CompanyNumberValidatorAPIView,
    CompanyPublicProfileViewSet,
    CompanySearchAPIView,
    CaseStudySearchAPIView,
    CompanyRetrieveUpdateAPIView,
    PublicCaseStudyViewSet,
    VerifyCompanyWithCodeAPIView,
    VerifyCompanyWithCompaniesHouseView,
    RemoveCollaboratorsView,
    CollaboratorInviteCreateView,
    TransferOwnershipInviteCreateView,
    CollaboratorInviteRetrieveUpdateAPIView,
    TransferOwnershipInviteRetrieveUpdateAPIView,
)
from notifications.views import (
    AnonymousUnsubscribeCreateAPIView,
)
from supplier.views import (
    GeckoTotalRegisteredSuppliersView,
    SupplierRetrieveExternalAPIView,
    SupplierRetrieveUpdateAPIView,
    SupplierSSOListExternalAPIView,
    UnsubscribeSupplierAPIView,
    CompanyCollboratorsListView,
)
from enrolment.views import (
    EnrolmentCreateAPIView,
    PreVerifiedEnrolmentRetrieveView,
)
from buyer.views import BuyerCreateAPIView
from contact.views import CreateMessageToSupplierAPIView
from exportopportunity import views as exportopportunity_views
from exportreadiness import views as exportreadiness_views

from django.conf import settings

admin.autodiscover()


urlpatterns = [
    url(
        r'^admin/',
        include(admin.site.urls)
    ),
    url(
        r'^$',
        HealthCheckAPIView.as_view(),
        name='health-check'
    ),
    url(
        r'^enrolment/$',
        EnrolmentCreateAPIView.as_view(),
        name='enrolment'
    ),
    url(
        r'^pre-verified-enrolment/$',
        PreVerifiedEnrolmentRetrieveView.as_view(),
        name='pre-verified-enrolment',
    ),
    url(
        r'^external/supplier-sso/$',
        SupplierSSOListExternalAPIView.as_view(),
        name='external-supplier-sso-list'
    ),
    url(
        r'^external/supplier/$',
        SupplierRetrieveExternalAPIView.as_view(),
        name='external-supplier-details'
    ),
    url(
        r'^supplier/gecko/total-registered/$',
        GeckoTotalRegisteredSuppliersView.as_view(),
        name='gecko-total-registered-suppliers'
    ),
    url(
        r'^supplier/company/$',
        CompanyRetrieveUpdateAPIView.as_view(),
        name='company'
    ),
    url(
        r'^supplier/company/verify/$',
        VerifyCompanyWithCodeAPIView.as_view(),
        name='company-verify'
    ),
    url(
        r'^supplier/company/verify/companies-house/$',
        VerifyCompanyWithCompaniesHouseView.as_view(),
        name='company-verify-companies-house'
    ),
    url(
        r'^supplier/company/case-study/$',
        CompanyCaseStudyViewSet.as_view({'post': 'create'}),
        name='company-case-study',
    ),
    url(
        r'^supplier/company/transfer-ownership-invite/(?P<uuid>.*)/$',
        TransferOwnershipInviteRetrieveUpdateAPIView.as_view(),
        name='transfer-ownership-invite-detail'
    ),
    url(
        r'^supplier/company/transfer-ownership-invite/$',
        TransferOwnershipInviteCreateView.as_view(),
        name='transfer-ownership-invite'
    ),
    url(
        r'^supplier/company/collaboration-invite/$',
        CollaboratorInviteCreateView.as_view(),
        name='collaboration-invite-create'
    ),
    url(
        r'^supplier/company/collaboration-invite/(?P<uuid>.*)/',
        CollaboratorInviteRetrieveUpdateAPIView.as_view(),
        name='collaboration-invite-detail'
    ),
    url(
        r'^supplier/company/remove-collaborators/',
        RemoveCollaboratorsView.as_view(),
        name='remove-collaborators'
    ),
    url(
        r'^supplier/company/case-study/(?P<pk>[0-9]+)/$',
        CompanyCaseStudyViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='company-case-study-detail',
    ),
    url(
        r'^supplier/company/collaborators/$',
        CompanyCollboratorsListView.as_view(),
        name='supplier-company-collaborators-list'
    ),
    url(
        r'^supplier/$',
        SupplierRetrieveUpdateAPIView.as_view(),
        name='supplier'
    ),
    url(
        r'^supplier/unsubscribe/$',
        UnsubscribeSupplierAPIView.as_view(),
        name='unsubscribe-supplier'
    ),
    url(
        r'^public/case-study/(?P<pk>.*)/$',
        PublicCaseStudyViewSet.as_view({'get': 'retrieve'}),
        name='public-case-study-detail'
    ),
    url(
        r'^public/company/(?P<companies_house_number>.*)/$',
        CompanyPublicProfileViewSet.as_view({'get': 'retrieve'}),
        name='company-public-profile-detail'
    ),
    url(
        r'^public/company/$',
        CompanyPublicProfileViewSet.as_view({'get': 'list'}),
        name='company-public-profile-list'
    ),
    url(
        r'^validate/company-number/$',
        CompanyNumberValidatorAPIView.as_view(),
        name='validate-company-number'
    ),
    url(
        r'^buyer/$',
        BuyerCreateAPIView.as_view(),
        name='buyer-create',
    ),
    url(
        r'^contact/supplier/$',
        CreateMessageToSupplierAPIView.as_view(),
        name='company-public-profile-contact-create'
    ),
    url(
        r'^notifications/anonymous-unsubscribe/$',
        AnonymousUnsubscribeCreateAPIView.as_view(),
        name='anonymous-unsubscribe'
    ),
    url(
        r'^company/search/$',
        CompanySearchAPIView.as_view(),
        name='company-search'
    ),
    url(
        r'^case-study/search/$',
        CaseStudySearchAPIView.as_view(),
        name='case-study-search',
    ),
    url(
        r'^export-opportunity/food/$',
        exportopportunity_views.ExportOpportunityFoodCreateAPIView.as_view(),
        name='export-opportunity-food-create'
    ),
    url(
        r'^export-opportunity/legal/$',
        exportopportunity_views.ExportOpportunityLegalCreateAPIView.as_view(),
        name='export-opportunity-legal-create'
    ),
    url(
        r'export-readiness/triage/$',
        exportreadiness_views.TriageResultCreateRetrieveView.as_view(),
        name='export-readiness-triage-create-retrieve'
    )
]

if settings.STORAGE_CLASS_NAME == 'local-storage':
    urlpatterns += [
        url(
            r'^media/(?P<path>.*)$',
            django.views.static.serve,
            {'document_root': settings.MEDIA_ROOT}
        ),
    ]
