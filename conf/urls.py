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
import enrolment.views
import exportplan.views
import notifications.views
import personalisation.views
import testapi.views
import exporting.views
import dataservices.views

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
    url(r'^healthcheck/', include((healthcheck_urls, 'healthcheck'), namespace='healthcheck')),
    url(r'^admin/', admin.site.urls),
    url(r'^activity-stream/', include((activity_stream_urls, 'activity-stream'), namespace='activity-stream')),
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
        company.views.CompanyUserSSOListAPIView.as_view(),
        name='external-supplier-sso-list'
    ),
    url(
        r'^external/supplier/$',
        company.views.CompanyUserRetrieveAPIView.as_view(),
        name='external-supplier-details'
    ),
    url(
        r'^supplier/gecko/total-registered/$',
        company.views.GeckoTotalRegisteredCompanyUser.as_view(),
        name='gecko-total-registered-suppliers'
    ),
    url(
        r'^supplier/(?P<sso_id>[0-9]+)/$',
        company.views.CompanyUserSSORetrieveAPIView.as_view(),
        name='supplier-retrieve-sso-id'
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
        r'^supplier/company/collaborator-invite/$',
        company.views.CollaborationInviteViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='collaboration-invite'
    ),
    url(
        r'^supplier/company/collaborator-invite/(?P<uuid>.*)/',
        company.views.CollaborationInviteViewSet.as_view({
            'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'
        }),
        name='collaboration-invite-detail'
    ),
    url(
        r'^supplier/company/remove-collaborators/',
        company.views.RemoveCollaboratorsView.as_view(),
        name='remove-collaborators'
    ),
    url(
        r'^supplier/company/disconnect/',
        company.views.CollaboratorDisconnectView.as_view(),
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
        company.views.CompanyCollboratorsListView.as_view(),
        name='supplier-company-collaborators-list'
    ),
    url(
        r'^supplier/company/collaborator-request/$',
        company.views.CollaborationRequestView.as_view(
            ({'post': 'create', 'get': 'list'})),
        name='collaborator-request'
    ),
    url(
        r'^supplier/company/collaborator-request/(?P<uuid>.*)/$',
        company.views.CollaborationRequestView.as_view(
            {'patch': 'partial_update', 'delete': 'destroy'}
        ),
        name='collaborator-request-detail'
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
        company.views.CompanyUserRetrieveUpdateAPIView.as_view(),
        name='supplier'
    ),
    url(
        r'^supplier/unsubscribe/$',
        company.views.CompanyUserUnsubscribeAPIView.as_view(),
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
        r'exporting/offices/(?P<postcode>.*)/$',
        exporting.views.RetrieveOfficesByPostCode.as_view(),
        name='offices-by-postcode'
    ),
    url(
        r'^personalisation/events/',
        personalisation.views.EventsView.as_view(),
        name='personalisation-events'
    ),
    url(
        r'^personalisation/export-opportunities/',
        personalisation.views.ExportOpportunitiesView.as_view(),
        name='personalisation-export-opportunities'
    ),
    url(
        r'^personalisation/user-location/$',
        personalisation.views.UserLocationCreateAPIView.as_view(),
        name='personalisation-user-location-create'
    ),
    url(
        r'^personalisation/recommended-countries/$',
        personalisation.views.RecommendedCountriesView.as_view(),
        name='personalisation-recommended-countries'
    ),
    url(
        r'^exportplan/company-export-plan/$',
        exportplan.views.CompanyExportPlanListCreateAPIView.as_view(),
        name='export-plan-list-create'
    ),
    url(
        r'^exportplan/company-export-plan/(?P<pk>[0-9]+)/$',
        exportplan.views.CompanyExportPlanRetrieveUpdateView.as_view(),
        name='export-plan-detail-update'
    ),
    url(
        r'^exportplan/company-objectives/(?P<pk>[0-9]+)/$',
        exportplan.views.CompanyObjectivesRetrieveUpdateDestroyView.as_view(),
        name='export-plan-objectives-detail-update'
    ),
    url(
        r'^exportplan/company-objectives/$',
        exportplan.views.CompanyObjectivesListCreateAPIView.as_view(),
        name='export-plan-objectives-list-create'
    ),
    url(
        r'^dataservices/easeofdoingbusiness/(?P<country_code>.*)/$',
        dataservices.views.RetrieveEaseOfBusinessIndex.as_view(),
        name='dataservices-easeofdoingbusiness-index'
    ),
    url(
        r'^dataservices/corruption-perceptions-index/(?P<country_code>.*)/$',
        dataservices.views.RetrieveCorruptionPerceptionsIndex.as_view(),
        name='dataservices-corruptionperceptionsindex'
    ),
    url(
        r'^dataservices/world-economic-outlook/(?P<country_code>.*)/$',
        dataservices.views.RetrieveWorldEconomicOutlook.as_view(),
        name='dataservices-world-economic-outlook'
    ),
    url(
        r'^dataservices/lastyearimportdata/$',
        dataservices.views.RetrieveLastYearImportDataView.as_view(),
        name='last-year-import-data'
    ),
    url(
        r'^dataservices/historicalimportdata/$',
        dataservices.views.RetrieveHistoricalImportDataView.as_view(),
        name='historical-import-data'
    ),
    url(
        r'^testapi/buyer/(?P<email>.*)/$',
        testapi.views.BuyerTestAPIView.as_view(),
        name='buyer_by_email'
    ),
    url(
        r'^testapi/test-buyers/$',
        testapi.views.BuyerTestAPIView.as_view(),
        name='delete_test_buyers'
    ),
    url(
        r'^testapi/company/(?P<ch_id_or_name>.*)/$',
        testapi.views.CompanyTestAPIView.as_view(),
        name='company_by_ch_id_or_name'
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
        r'^testapi/test-companies/$',
        testapi.views.AutomatedTestsCompaniesTestAPIView.as_view(),
        name='delete_test_companies'
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
elif settings.STORAGE_CLASS_NAME == 'default':
    urlpatterns += [
        url(
            r'buyer/csv-dump/$',
            buyer.views.BuyerCSVDownloadAPIView.as_view(),
            name='buyer-csv-dump'
        ),
        url(
            r'supplier/csv-dump/$',
            company.views.CompanyUserCSVDownloadAPIView.as_view(),
            name='supplier-csv-dump'
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
