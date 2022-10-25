import directory_healthcheck.views
import django
from django.conf import settings
from django.conf.urls import include, url
from django.contrib import admin
from django.urls import reverse_lazy
from django.views.generic import RedirectView

import activitystream.views
import buyer.views
import company.views
import dataservices.views
import enrolment.views
import exporting.views
import exportplan.views
import notifications.views
import personalisation.views
import testapi.views

admin.autodiscover()

healthcheck_urls = [
    url(r'^$', directory_healthcheck.views.HealthcheckView.as_view(), name='healthcheck'),
    url(r'^ping/$', directory_healthcheck.views.PingView.as_view(), name='ping'),
]

activity_stream_urls = [
    url(r'^$', activitystream.views.ActivityStreamViewSet.as_view({'get': 'list'}), name='activity-stream'),
    url(
        r'^company/$',
        activitystream.views.ActivityStreamCompanyViewSet.as_view({'get': 'list'}),
        name='activity-stream-companies',
    ),
    url(
        r'^exportplan/$',
        activitystream.views.ActivityStreamExportPlanDataViewSet.as_view({'get': 'list'}),
        name='activity-stream-export-plan-data',
    ),
]


urlpatterns = [
    url(r'^healthcheck/', include((healthcheck_urls, 'healthcheck'), namespace='healthcheck')),
    url(r'^admin/', admin.site.urls),
    url(r'^activity-stream/', include((activity_stream_urls, 'activity-stream'), namespace='activity-stream')),
    url(r'^enrolment/$', enrolment.views.EnrolmentCreateAPIView.as_view(), name='enrolment'),
    url(
        r'^pre-verified-enrolment/$',
        enrolment.views.PreVerifiedEnrolmentRetrieveView.as_view(),
        name='pre-verified-enrolment',
    ),
    url(
        r'^external/supplier-sso/$',
        company.views.CompanyUserSSOListAPIView.as_view(),
        name='external-supplier-sso-list',
    ),
    url(r'^external/supplier/$', company.views.CompanyUserRetrieveAPIView.as_view(), name='external-supplier-details'),
    url(
        r'^supplier/gecko/total-registered/$',
        company.views.GeckoTotalRegisteredCompanyUser.as_view(),
        name='gecko-total-registered-suppliers',
    ),
    url(
        r'^supplier/(?P<sso_id>[0-9]+)/$',
        company.views.CompanyUserSSORetrieveAPIView.as_view(),
        name='supplier-retrieve-sso-id',
    ),
    url(r'^supplier/company/$', company.views.CompanyRetrieveUpdateAPIView.as_view(), name='company'),
    url(
        r'^supplier/company/(?P<sso_id>[0-9]+)/(?P<request_key>.*)/$',
        company.views.CompanyDestroyAPIView.as_view(),
        name='company-delete-by-sso-id',
    ),
    url(r'^supplier/company/verify/$', company.views.VerifyCompanyWithCodeAPIView.as_view(), name='company-verify'),
    url(
        r'^supplier/company/verify/companies-house/$',
        company.views.VerifyCompanyWithCompaniesHouseView.as_view(),
        name='company-verify-companies-house',
    ),
    url(
        r'^supplier/company/verify/identity/$',
        company.views.RequestVerificationWithIdentificationView.as_view(),
        name='company-verify-identity',
    ),
    url(
        r'^supplier/company/case-study/$',
        company.views.CompanyCaseStudyViewSet.as_view({'post': 'create'}),
        name='company-case-study',
    ),
    url(
        r'^supplier/company/collaborator-invite/$',
        company.views.CollaborationInviteViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='collaboration-invite',
    ),
    url(
        r'^supplier/company/collaborator-invite/(?P<uuid>.*)/',
        company.views.CollaborationInviteViewSet.as_view(
            {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
        ),
        name='collaboration-invite-detail',
    ),
    url(
        r'^supplier/company/remove-collaborators/',
        company.views.RemoveCollaboratorsView.as_view(),
        name='remove-collaborators',
    ),
    url(
        r'^supplier/company/disconnect/',
        company.views.CollaboratorDisconnectView.as_view(),
        name='company-disconnect-supplier',
    ),
    url(
        r'^supplier/company/case-study/(?P<pk>[0-9]+)/$',
        company.views.CompanyCaseStudyViewSet.as_view(
            {
                'get': 'retrieve',
                'patch': 'partial_update',
                'delete': 'destroy',
            }
        ),
        name='company-case-study-detail',
    ),
    url(
        r'^supplier/company/collaborators/$',
        company.views.CompanyCollboratorsListView.as_view(),
        name='supplier-company-collaborators-list',
    ),
    url(
        r'^supplier/company/collaborator-request/$',
        company.views.CollaborationRequestView.as_view(({'post': 'create', 'get': 'list'})),
        name='collaborator-request',
    ),
    url(
        r'^supplier/company/collaborator-request/(?P<uuid>.*)/$',
        company.views.CollaborationRequestView.as_view({'patch': 'partial_update', 'delete': 'destroy'}),
        name='collaborator-request-detail',
    ),
    url(
        r'^supplier/company/add-collaborator/$',
        company.views.AddCollaboratorView.as_view(),
        name='register-company-collaborator-request',
    ),
    url(
        r'^supplier/company/change-collaborator-role/(?P<sso_id>\d+)/$',
        company.views.ChangeCollaboratorRoleView.as_view(),
        name='change-collaborator-role',
    ),
    url(r'^supplier/$', company.views.CompanyUserRetrieveUpdateAPIView.as_view(), name='supplier'),
    url(r'^supplier/unsubscribe/$', company.views.CompanyUserUnsubscribeAPIView.as_view(), name='unsubscribe-supplier'),
    url(
        r'^public/case-study/(?P<pk>.*)/$',
        company.views.PublicCaseStudyViewSet.as_view({'get': 'retrieve'}),
        name='public-case-study-detail',
    ),
    url(
        r'^public/company/(?P<companies_house_number>.*)/$',
        company.views.CompanyPublicProfileViewSet.as_view({'get': 'retrieve'}),
        name='company-public-profile-detail',
    ),
    url(
        r'^validate/company-number/$',
        company.views.CompanyNumberValidatorAPIView.as_view(),
        name='validate-company-number',
    ),
    url(
        r'^buyer/$',
        buyer.views.BuyerCreateAPIView.as_view(),
        name='buyer-create',
    ),
    url(
        r'^notifications/anonymous-unsubscribe/$',
        notifications.views.AnonymousUnsubscribeCreateAPIView.as_view(),
        name='anonymous-unsubscribe',
    ),
    url(r'^company/search/$', company.views.FindASupplierSearchAPIView.as_view(), name='find-a-supplier-search'),
    url(
        r'^investment-support-directory/search/$',
        company.views.InvestmentSupportDirectorySearchAPIView.as_view(),
        name='investment-support-directory-search',
    ),
    url(
        r'exporting/offices/(?P<postcode>.*)/$',
        exporting.views.RetrieveOfficesByPostCode.as_view(),
        name='offices-by-postcode',
    ),
    url(r'^personalisation/events/', personalisation.views.EventsView.as_view(), name='personalisation-events'),
    url(
        r'^personalisation/export-opportunities/',
        personalisation.views.ExportOpportunitiesView.as_view(),
        name='personalisation-export-opportunities',
    ),
    url(
        r'^personalisation/user-location/$',
        personalisation.views.UserLocationCreateAPIView.as_view(),
        name='personalisation-user-location-create',
    ),
    url(
        r'^personalisation/recommended-countries/$',
        personalisation.views.RecommendedCountriesView.as_view(),
        name='personalisation-recommended-countries',
    ),
    url(
        r'^dataservices/suggested-countries/$',
        dataservices.views.SuggestedCountriesView.as_view(),
        name='dataservices-suggested-countries',
    ),
    url(
        r'^dataservices/trading-blocs/$',
        dataservices.views.TradingBlocsView.as_view(),
        name='dataservices-trading-blocs',
    ),
    url(
        r'^dataservices/trade-barriers/$',
        dataservices.views.TradeBarriersView.as_view(),
        name='dataservices-trade-barriers',
    ),
    url(
        r'^exportplan/detail-list/',
        exportplan.views.ExportPlanListAPIView.as_view(),
        name='export-plan-detail-list',
    ),
    url(
        r'^exportplan/create/',
        exportplan.views.ExportPlanCreateAPIView.as_view(),
        name='export-plan-create',
    ),
    url(
        r'^exportplan/company-export-plan/(?P<pk>[0-9]+)/$',
        exportplan.views.CompanyExportPlanRetrieveUpdateView.as_view(),
        name='export-plan-detail-update',
    ),
    url(
        r'^exportplan/export-plan-model-object-list-create/$',
        exportplan.views.ExportPlanModelObjectListCreateAPIView.as_view(),
        name='export-plan-model-object-list-create',
    ),
    url(
        r'^exportplan/export-plan-model-object-update-delete/(?P<pk>[0-9]+)/$',
        exportplan.views.ExportPlanModelObjectRetrieveUpdateDestroyView.as_view(),
        name='export-plan-model-object-update-delete',
    ),
    url(
        r'^exportplan/export-plan-model-object-detail/(?P<pk>[0-9]+)/(?P<model_name>.*)/$',
        exportplan.views.ExportPlanModelObjectRetrieveUpdateDestroyView.as_view(),
        name='export-plan-model-object-detail',
    ),
    url(
        r'^exportplan/pdf-upload/$',
        exportplan.views.ExportPlanUploadFile.as_view(),
        name='export-plan-pdf-upload',
    ),
    url(
        r'^dataservices/country-data/$',
        dataservices.views.RetrieveDataByCountryView.as_view(),
        name='dataservices-country-data-by-country',
    ),
    url(
        r'^dataservices/lastyearimportdatabycountry/$',
        dataservices.views.RetrieveLastYearImportDataByCountryView.as_view(),
        name='last-year-import-data-by-country',
    ),
    url(
        r'^dataservices/cia-factbook-data/$',
        dataservices.views.RetrieveCiaFactbooklDataView.as_view(),
        name='cia-factbook-data',
    ),
    url(
        r'^dataservices/society-data-by-country/$',
        dataservices.views.RetrieveSocietyDataByCountryView.as_view(),
        name='dataservices-society-data-by-country',
    ),
    url(
        r'^dataservices/top-five-goods/$',
        dataservices.views.TopFiveGoodsExportsByCountryView.as_view(),
        name='dataservices-top-five-goods-by-country',
    ),
    url(
        r'^dataservices/top-five-services/$',
        dataservices.views.TopFiveServicesExportsByCountryView.as_view(),
        name='dataservices-top-five-services-by-country',
    ),
    url(
        r'^dataservices/uk-market-trends/$',
        dataservices.views.UKMarketTrendsView.as_view(),
        name='dataservices-market-trends',
    ),
    url(
        r'^dataservices/uk-trade-highlights/$',
        dataservices.views.UKTradeHighlightsView.as_view(),
        name='dataservices-trade-highlights',
    ),
    url(
        r'^dataservices/economic-highlights/$',
        dataservices.views.EconomicHighlightsView.as_view(),
        name='dataservices-economic-highlights',
    ),
    url(
        r'^dataservices/uk-free-trade-agreements/$',
        dataservices.views.UKFreeTradeAgreementsView.as_view(),
        name='dataservices-trade-agreements',
    ),
    url(r'^testapi/buyer/(?P<email>.*)/$', testapi.views.BuyerTestAPIView.as_view(), name='buyer_by_email'),
    url(r'^testapi/test-buyers/$', testapi.views.BuyerTestAPIView.as_view(), name='delete_test_buyers'),
    url(
        r'^testapi/company/(?P<ch_id_or_name>.*)/$',
        testapi.views.CompanyTestAPIView.as_view(),
        name='company_by_ch_id_or_name',
    ),
    url(r'^testapi/isd_company/$', testapi.views.ISDCompanyTestAPIView.as_view(), name='create_test_isd_company'),
    url(
        r'^testapi/companies/published/$',
        testapi.views.PublishedCompaniesTestAPIView.as_view(),
        name='published_companies',
    ),
    url(
        r'^testapi/companies/unpublished/$',
        testapi.views.UnpublishedCompaniesTestAPIView.as_view(),
        name='unpublished_companies',
    ),
    url(
        r'^testapi/test-companies/$',
        testapi.views.AutomatedTestsCompaniesTestAPIView.as_view(),
        name='delete_test_companies',
    ),
    url(
        r'^enrolment/preverified-company/(?P<key>.*)/claim/$',
        enrolment.views.PreverifiedCompanyClaim.as_view(),
        name='enrolment-claim-preverified',
    ),
    url(
        r'^enrolment/preverified-company/(?P<key>.*)/$',
        enrolment.views.PreverifiedCompanyView.as_view(),
        name='enrolment-preverified',
    ),
]

if settings.STORAGE_CLASS_NAME == 'local-storage':
    urlpatterns += [
        url(r'^media/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT}, name='media'),
    ]
elif settings.STORAGE_CLASS_NAME == 'default':
    urlpatterns += [
        url(r'buyer/csv-dump/$', buyer.views.BuyerCSVDownloadAPIView.as_view(), name='buyer-csv-dump'),
        url(r'supplier/csv-dump/$', company.views.CompanyUserCSVDownloadAPIView.as_view(), name='supplier-csv-dump'),
    ]


if settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    authbroker_urls = [
        url(
            r'^admin/login/$',
            RedirectView.as_view(
                url=reverse_lazy('authbroker_client:login'),
                query_string=True,
            ),
        ),
        url('^auth/', include('authbroker_client.urls')),
    ]

    urlpatterns = [url('^', include(authbroker_urls))] + urlpatterns
