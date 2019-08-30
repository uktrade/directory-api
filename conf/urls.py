import directory_healthcheck.views

import django
from django.conf import settings
from django.conf.urls import url, include
from django.contrib import admin
from django.urls import reverse_lazy
from django.views.generic import RedirectView

import activitystream.views
import buyer.views
import company.views
import contact.views
import enrolment.views
import notifications.views
import supplier.views
import testapi.views
import exporting.views


admin.autodiscover()

healthcheck_urls = [
    url(
        r'^$',
        directory_healthcheck.views.HealthcheckView.as_view(),
        name='healthcheck'
    ),
    url(
        r'^ping/$',
        directory_healthcheck.views.PingView.as_view(),
        name='ping'
    ),
]

activity_stream_urls = [
    url(
        r'^$',
        activitystream.views.ActivityStreamViewSet.as_view({'get': 'list'}),
        name='activity-stream'
    ),
]


urlpatterns = [
    url(
        r'^healthcheck/',
        include(
            healthcheck_urls,
            namespace='healthcheck',
            app_name='healthcheck',
        )
    ),
    url(
        r'^admin/',
        include(admin.site.urls)
    ),
    url(
        r'^activity-stream/',
        include(
            activity_stream_urls,
            namespace='activity-stream',
            app_name='activity-stream',
        )
    ),
    url(
        r'^enrolment/$',
        enrolment.views.EnrolmentCreateAPIView.as_view(),
        name='enrolment'
    ),
    url(
        r'^pre-verified-enrolment/$',
        enrolment.views.PreVerifiedEnrolmentRetrieveView.as_view(),
        name='pre-verified-enrolment',
    ),
    url(
        r'^external/supplier-sso/$',
        supplier.views.SupplierSSOListExternalAPIView.as_view(),
        name='external-supplier-sso-list'
    ),
    url(
        r'^external/supplier/$',
        supplier.views.SupplierRetrieveExternalAPIView.as_view(),
        name='external-supplier-details'
    ),
    url(
        r'^supplier/gecko/total-registered/$',
        supplier.views.GeckoTotalRegisteredSuppliersView.as_view(),
        name='gecko-total-registered-suppliers'
    ),
    url(
        r'^supplier/company/$',
        company.views.CompanyRetrieveUpdateAPIView.as_view(),
        name='company'
    ),
    url(
        r'^supplier/company/verify/$',
        company.views.VerifyCompanyWithCodeAPIView.as_view(),
        name='company-verify'
    ),
    url(
        r'^supplier/company/verify/companies-house/$',
        company.views.VerifyCompanyWithCompaniesHouseView.as_view(),
        name='company-verify-companies-house'
    ),
    url(
        r'^supplier/company/verify/identity/$',
        company.views.RequestVerificationWithIdentificationView.as_view(),
        name='company-verify-identity'
    ),
    url(
        r'^supplier/company/case-study/$',
        company.views.CompanyCaseStudyViewSet.as_view({'post': 'create'}),
        name='company-case-study',
    ),
    url(
        r'^supplier/company/transfer-ownership-invite/(?P<uuid>.*)/$',
        company.views.TransferOwnershipInviteRetrieveUpdateAPIView.as_view(),
        name='old-transfer-ownership-invite-detail'
    ),
    url(
        r'^supplier/company/transfer-ownership-invite/$',
        company.views.TransferOwnershipInviteCreateView.as_view(),
        name='old-transfer-ownership-invite'
    ),
    url(
        r'^supplier/company/collaboration-invite/$',
        company.views.CollaboratorInviteCreateView.as_view(),
        name='old-collaboration-invite-create'
    ),
    url(
        r'^supplier/company/collaboration-invite/(?P<uuid>.*)/',
        company.views.CollaboratorInviteRetrieveUpdateAPIView.as_view(),
        name='old-collaboration-invite-detail'
    ),
    url(
        r'^supplier/company/collaborator-invite/$',
        company.views.CollaborationInviteViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='collaboration-invite'
    ),
    url(
        r'^supplier/company/collaborator-invite/(?P<uuid>.*)/',
        company.views.CollaborationInviteViewSet.as_view({
            'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'
        }),
        name='collaboration-invite-retrieve'
    ),
    url(
        r'^supplier/company/remove-collaborators/',
        company.views.RemoveCollaboratorsView.as_view(),
        name='remove-collaborators'
    ),
    url(
        r'^supplier/company/disconnect/',
        supplier.views.CollaboratorDisconnectView.as_view(),
        name='company-disconnect-supplier'
    ),
    url(
        r'^supplier/company/case-study/(?P<pk>[0-9]+)/$',
        company.views.CompanyCaseStudyViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='company-case-study-detail',
    ),
    url(
        r'^supplier/company/collaborators/$',
        supplier.views.CompanyCollboratorsListView.as_view(),
        name='supplier-company-collaborators-list'
    ),
    url(
        r'^supplier/company/collaborator-request/$',
        company.views.CollaboratorRequestView.as_view(),
        name='collaborator-request'
    ),
    url(
        r'^supplier/company/add-collaborator/$',
        company.views.AddCollaboratorView.as_view(),
        name='register-company-collaborator-request'
    ),
    url(
        r'^supplier/company/change-collaborator-role/(?P<sso_id>\d+)/$',
        company.views.ChangeCollaboratorRoleView.as_view(),
        name='change-collaborator-role'
    ),
    url(
        r'^supplier/$',
        supplier.views.SupplierRetrieveUpdateAPIView.as_view(),
        name='supplier'
    ),
    url(
        r'^supplier/unsubscribe/$',
        supplier.views.UnsubscribeSupplierAPIView.as_view(),
        name='unsubscribe-supplier'
    ),
    url(
        r'^public/case-study/(?P<pk>.*)/$',
        company.views.PublicCaseStudyViewSet.as_view({'get': 'retrieve'}),
        name='public-case-study-detail'
    ),
    url(
        r'^public/company/(?P<companies_house_number>.*)/$',
        company.views.CompanyPublicProfileViewSet.as_view({'get': 'retrieve'}),
        name='company-public-profile-detail'
    ),
    url(
        r'^validate/company-number/$',
        company.views.CompanyNumberValidatorAPIView.as_view(),
        name='validate-company-number'
    ),
    url(
        r'^buyer/$',
        buyer.views.BuyerCreateAPIView.as_view(),
        name='buyer-create',
    ),
    url(
        r'^contact/supplier/$',
        contact.views.CreateMessageToSupplierAPIView.as_view(),
        name='company-public-profile-contact-create'
    ),
    url(
        r'^notifications/anonymous-unsubscribe/$',
        notifications.views.AnonymousUnsubscribeCreateAPIView.as_view(),
        name='anonymous-unsubscribe'
    ),
    url(
        r'^company/search/$',
        company.views.FindASupplierSearchAPIView.as_view(),
        name='find-a-supplier-search'
    ),
    url(
        r'^investment-support-directory/search/$',
        company.views.InvestmentSupportDirectorySearchAPIView.as_view(),
        name='investment-support-directory-search'
    ),
    url(
        r'buyer/csv-dump/$',
        buyer.views.BuyerCSVDownloadAPIView.as_view(),
        name='buyer-csv-dump'
    ),
    url(
        r'supplier/csv-dump/$',
        supplier.views.SupplierCSVDownloadAPIView.as_view(),
        name='supplier-csv-dump'
    ),
    url(
        r'exporting/offices/(?P<postcode>.*)/$',
        exporting.views.RetrieveOfficesByPostCode.as_view(),
        name='offices-by-postcode'
    ),
    url(
        r'^testapi/company/(?P<ch_id>.*)/$',
        testapi.views.CompanyTestAPIView.as_view(),
        name='company_by_ch_id'
    ),
    url(
        r'^testapi/isd_company/$',
        testapi.views.ISDCompanyTestAPIView.as_view(),
        name='create_test_isd_company'
    ),
    url(
        r'^testapi/companies/published/$',
        testapi.views.PublishedCompaniesTestAPIView.as_view(),
        name='published_companies'
    ),
    url(
        r'^testapi/companies/unpublished/$',
        testapi.views.UnpublishedCompaniesTestAPIView.as_view(),
        name='unpublished_companies'
    ),
    url(
        r'^enrolment/preverified-company/(?P<key>.*)/claim/$',
        enrolment.views.PreverifiedCompanyClaim.as_view(),
        name='enrolment-claim-preverified'
    ),
    url(
        r'^enrolment/preverified-company/(?P<key>.*)/$',
        enrolment.views.PreverifiedCompanyView.as_view(),
        name='enrolment-preverified'
    ),
]

if settings.STORAGE_CLASS_NAME == 'local-storage':
    urlpatterns += [
        url(
            r'^media/(?P<path>.*)$',
            django.views.static.serve,
            {'document_root': settings.MEDIA_ROOT},
            name='media'
        ),
    ]


if settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    authbroker_urls = [
        url(
            r'^admin/login/$',
            RedirectView.as_view(url=reverse_lazy('authbroker_client:login'),
                                 query_string=True, )
        ),
        url('^auth/', include('authbroker_client.urls')),
    ]

    urlpatterns = [url('^', include(authbroker_urls))] + urlpatterns
