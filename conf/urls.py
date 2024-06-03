import directory_healthcheck.views
import django
from django.conf import settings
from django.conf.urls import include
from django.contrib import admin
from django.urls import path, re_path, reverse_lazy
from django.views.generic import RedirectView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

import activitystream.views
import buyer.views
import company.views
import dataservices.views
import enrolment.views
import exporting.views
import exportplan.views
import notifications.views
import personalisation.views
import survey.views
import testapi.views
from core.views import PingDomView

admin.autodiscover()

healthcheck_urls = [
    re_path(r'^$', directory_healthcheck.views.HealthcheckView.as_view(), name='healthcheck'),
    re_path(r'^ping/$', directory_healthcheck.views.PingView.as_view(), name='ping'),
]

activity_stream_urls = [
    re_path(r'^$', activitystream.views.ActivityStreamViewSet.as_view({'get': 'list'}), name='activity-stream'),
    re_path(
        r'^company/$',
        activitystream.views.ActivityStreamCompanyViewSet.as_view({'get': 'list'}),
        name='activity-stream-companies',
    ),
    re_path(
        r'^exportplan/$',
        activitystream.views.ActivityStreamExportPlanView.as_view(),
        name='activity-stream-export-plan-data',
    ),
]


urlpatterns = [
    re_path(r'^healthcheck/', include((healthcheck_urls, 'healthcheck'), namespace='healthcheck')),
    path('pingdom/ping.xml', PingDomView.as_view(), name='pingdom'),
    re_path(r'^admin/', admin.site.urls),
    re_path(r'^activity-stream/', include((activity_stream_urls, 'activity-stream'), namespace='activity-stream')),
    re_path(r'^enrolment/$', enrolment.views.EnrolmentCreateAPIView.as_view(), name='enrolment'),
    re_path(
        r'^pre-verified-enrolment/$',
        enrolment.views.PreVerifiedEnrolmentRetrieveView.as_view(),
        name='pre-verified-enrolment',
    ),
    re_path(
        r'^external/supplier-sso/$',
        company.views.CompanyUserSSOListAPIView.as_view(),
        name='external-supplier-sso-list',
    ),
    re_path(
        r'^external/supplier/$', company.views.CompanyUserRetrieveAPIView.as_view(), name='external-supplier-details'
    ),
    re_path(
        r'^supplier/gecko/total-registered/$',
        company.views.GeckoTotalRegisteredCompanyUser.as_view(),
        name='gecko-total-registered-suppliers',
    ),
    re_path(
        r'^supplier/(?P<sso_id>[0-9]+)/$',
        company.views.CompanyUserSSORetrieveAPIView.as_view(),
        name='supplier-retrieve-sso-id',
    ),
    re_path(r'^supplier/company/$', company.views.CompanyRetrieveUpdateAPIView.as_view(), name='company'),
    re_path(
        r'^supplier/company/(?P<sso_id>[0-9]+)/(?P<request_key>.*)/$',
        company.views.CompanyDestroyAPIView.as_view(),
        name='company-delete-by-sso-id',
    ),
    re_path(r'^supplier/company/verify/$', company.views.VerifyCompanyWithCodeAPIView.as_view(), name='company-verify'),
    re_path(
        r'^supplier/company/verify/companies-house/$',
        company.views.VerifyCompanyWithCompaniesHouseView.as_view(),
        name='company-verify-companies-house',
    ),
    re_path(
        r'^supplier/company/verify/identity/$',
        company.views.RequestVerificationWithIdentificationView.as_view(),
        name='company-verify-identity',
    ),
    re_path(
        r'^supplier/company/case-study/$',
        company.views.CompanyCaseStudyViewSet.as_view({'post': 'create'}),
        name='company-case-study',
    ),
    re_path(
        r'^supplier/company/collaborator-invite/$',
        company.views.CollaborationInviteViewSet.as_view({'post': 'create', 'get': 'list'}),
        name='collaboration-invite',
    ),
    re_path(
        r'^supplier/company/collaborator-invite/(?P<uuid>.*)/',
        company.views.CollaborationInviteViewSet.as_view(
            {'get': 'retrieve', 'patch': 'partial_update', 'delete': 'destroy'}
        ),
        name='collaboration-invite-detail',
    ),
    re_path(
        r'^supplier/company/remove-collaborators/',
        company.views.RemoveCollaboratorsView.as_view(),
        name='remove-collaborators',
    ),
    re_path(
        r'^supplier/company/disconnect/',
        company.views.CollaboratorDisconnectView.as_view(),
        name='company-disconnect-supplier',
    ),
    re_path(
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
    re_path(
        r'^supplier/company/collaborators/$',
        company.views.CompanyCollboratorsListView.as_view(),
        name='supplier-company-collaborators-list',
    ),
    re_path(
        r'^supplier/company/collaborator-request/$',
        company.views.CollaborationRequestView.as_view(({'post': 'create', 'get': 'list'})),
        name='collaborator-request',
    ),
    re_path(
        r'^supplier/company/collaborator-request/(?P<uuid>.*)/$',
        company.views.CollaborationRequestView.as_view({'patch': 'partial_update', 'delete': 'destroy'}),
        name='collaborator-request-detail',
    ),
    re_path(
        r'^supplier/company/add-collaborator/$',
        company.views.AddCollaboratorView.as_view(),
        name='register-company-collaborator-request',
    ),
    re_path(
        r'^supplier/company/change-collaborator-role/(?P<sso_id>\d+)/$',
        company.views.ChangeCollaboratorRoleView.as_view(),
        name='change-collaborator-role',
    ),
    re_path(r'^supplier/$', company.views.CompanyUserRetrieveUpdateAPIView.as_view(), name='supplier'),
    re_path(
        r'^supplier/unsubscribe/$', company.views.CompanyUserUnsubscribeAPIView.as_view(), name='unsubscribe-supplier'
    ),
    re_path(
        r'^public/case-study/(?P<pk>.*)/$',
        company.views.PublicCaseStudyViewSet.as_view({'get': 'retrieve'}),
        name='public-case-study-detail',
    ),
    re_path(
        r'^public/company/(?P<companies_house_number>.*)/$',
        company.views.CompanyPublicProfileViewSet.as_view({'get': 'retrieve'}),
        name='company-public-profile-detail',
    ),
    re_path(
        r'^validate/company-number/$',
        company.views.CompanyNumberValidatorAPIView.as_view(),
        name='validate-company-number',
    ),
    re_path(
        r'^buyer/$',
        buyer.views.BuyerCreateAPIView.as_view(),
        name='buyer-create',
    ),
    re_path(
        r'^notifications/anonymous-unsubscribe/$',
        notifications.views.AnonymousUnsubscribeCreateAPIView.as_view(),
        name='anonymous-unsubscribe',
    ),
    re_path(r'^company/search/$', company.views.FindASupplierSearchAPIView.as_view(), name='find-a-supplier-search'),
    re_path(
        r'^investment-support-directory/search/$',
        company.views.InvestmentSupportDirectorySearchAPIView.as_view(),
        name='investment-support-directory-search',
    ),
    re_path(
        r'exporting/offices/(?P<postcode>.*)/$',
        exporting.views.RetrieveOfficesByPostCode.as_view(),
        name='offices-by-postcode',
    ),
    re_path(r'^personalisation/events/', personalisation.views.EventsView.as_view(), name='personalisation-events'),
    re_path(
        r'^personalisation/export-opportunities/',
        personalisation.views.ExportOpportunitiesView.as_view(),
        name='personalisation-export-opportunities',
    ),
    re_path(
        r'^personalisation/user-location/$',
        personalisation.views.UserLocationCreateAPIView.as_view(),
        name='personalisation-user-location-create',
    ),
    re_path(
        r'^personalisation/recommended-countries/$',
        personalisation.views.RecommendedCountriesView.as_view(),
        name='personalisation-recommended-countries',
    ),
    re_path(
        r'^dataservices/suggested-countries/$',
        dataservices.views.SuggestedCountriesView.as_view(),
        name='dataservices-suggested-countries',
    ),
    re_path(
        r'^dataservices/trading-blocs/$',
        dataservices.views.TradingBlocsView.as_view(),
        name='dataservices-trading-blocs',
    ),
    re_path(
        r'^dataservices/trade-barriers/$',
        dataservices.views.TradeBarriersView.as_view(),
        name='dataservices-trade-barriers',
    ),
    re_path(
        r'^exportplan/detail-list/',
        exportplan.views.ExportPlanListAPIView.as_view(),
        name='export-plan-detail-list',
    ),
    re_path(
        r'^exportplan/create/',
        exportplan.views.ExportPlanCreateAPIView.as_view(),
        name='export-plan-create',
    ),
    re_path(
        r'^exportplan/company-export-plan/(?P<pk>[0-9]+)/$',
        exportplan.views.CompanyExportPlanRetrieveUpdateView.as_view(),
        name='export-plan-detail-update',
    ),
    re_path(
        r'^exportplan/export-plan-model-object-list-create/$',
        exportplan.views.ExportPlanModelObjectListCreateAPIView.as_view(),
        name='export-plan-model-object-list-create',
    ),
    re_path(
        r'^exportplan/export-plan-model-object-update-delete/(?P<pk>[0-9]+)/$',
        exportplan.views.ExportPlanModelObjectRetrieveUpdateDestroyView.as_view(),
        name='export-plan-model-object-update-delete',
    ),
    re_path(
        r'^exportplan/export-plan-model-object-detail/(?P<pk>[0-9]+)/(?P<model_name>.*)/$',
        exportplan.views.ExportPlanModelObjectRetrieveUpdateDestroyView.as_view(),
        name='export-plan-model-object-detail',
    ),
    re_path(
        r'^exportplan/pdf-upload/$',
        exportplan.views.ExportPlanUploadFile.as_view(),
        name='export-plan-pdf-upload',
    ),
    re_path(
        r'^dataservices/country-data/$',
        dataservices.views.RetrieveDataByCountryView.as_view(),
        name='dataservices-country-data-by-country',
    ),
    re_path(
        r'^dataservices/markets/$',
        dataservices.views.RetrieveMarketsView.as_view(),
        name='dataservices-markets',
    ),
    re_path(
        r'^dataservices/lastyearimportdatabycountry/$',
        dataservices.views.RetrieveLastYearImportDataByCountryView.as_view(),
        name='last-year-import-data-by-country',
    ),
    re_path(
        r'^dataservices/cia-factbook-data/$',
        dataservices.views.RetrieveCiaFactbooklDataView.as_view(),
        name='cia-factbook-data',
    ),
    re_path(
        r'^dataservices/society-data-by-country/$',
        dataservices.views.RetrieveSocietyDataByCountryView.as_view(),
        name='dataservices-society-data-by-country',
    ),
    re_path(
        r'^dataservices/top-five-goods/$',
        dataservices.views.TopFiveGoodsExportsByCountryView.as_view(),
        name='dataservices-top-five-goods-by-country',
    ),
    re_path(
        r'^dataservices/top-five-services/$',
        dataservices.views.TopFiveServicesExportsByCountryView.as_view(),
        name='dataservices-top-five-services-by-country',
    ),
    re_path(
        r'^dataservices/uk-market-trends/$',
        dataservices.views.UKMarketTrendsView.as_view(),
        name='dataservices-market-trends',
    ),
    re_path(
        r'^dataservices/uk-trade-highlights/$',
        dataservices.views.UKTradeHighlightsView.as_view(),
        name='dataservices-trade-highlights',
    ),
    re_path(
        r'^dataservices/economic-highlights/$',
        dataservices.views.EconomicHighlightsView.as_view(),
        name='dataservices-economic-highlights',
    ),
    re_path(
        r'^dataservices/uk-free-trade-agreements/$',
        dataservices.views.UKFreeTradeAgreementsView.as_view(),
        name='dataservices-trade-agreements',
    ),
    re_path(
        r'^dataservices/business-cluster-information-by-sic/$',
        dataservices.views.BusinessClusterInformationBySicView.as_view(),
        name='dataservices-business-cluster-information-by-sic',
    ),
    re_path(
        r'^dataservices/business-cluster-information-by-dbt-sector/$',
        dataservices.views.BusinessClusterInformationByDBTSectorView.as_view(),
        name='dataservices-business-cluster-information-by-dbt-sector',
    ),
    re_path(r'^testapi/buyer/(?P<email>.*)/$', testapi.views.BuyerTestAPIView.as_view(), name='buyer_by_email'),
    re_path(r'^testapi/test-buyers/$', testapi.views.BuyerTestAPIView.as_view(), name='delete_test_buyers'),
    re_path(
        r'^testapi/company/(?P<ch_id_or_name>.*)/$',
        testapi.views.CompanyTestAPIView.as_view(),
        name='company_by_ch_id_or_name',
    ),
    re_path(r'^testapi/isd_company/$', testapi.views.ISDCompanyTestAPIView.as_view(), name='create_test_isd_company'),
    re_path(
        r'^testapi/companies/published/$',
        testapi.views.PublishedCompaniesTestAPIView.as_view(),
        name='published_companies',
    ),
    re_path(
        r'^testapi/companies/unpublished/$',
        testapi.views.UnpublishedCompaniesTestAPIView.as_view(),
        name='unpublished_companies',
    ),
    re_path(
        r'^testapi/test-companies/$',
        testapi.views.AutomatedTestsCompaniesTestAPIView.as_view(),
        name='delete_test_companies',
    ),
    re_path(
        r'^enrolment/preverified-company/(?P<key>.*)/claim/$',
        enrolment.views.PreverifiedCompanyClaim.as_view(),
        name='enrolment-claim-preverified',
    ),
    re_path(
        r'^enrolment/preverified-company/(?P<key>.*)/$',
        enrolment.views.PreverifiedCompanyView.as_view(),
        name='enrolment-preverified',
    ),
    re_path(r'^survey/(?P<pk>.*)', survey.views.SurveyDetailView.as_view(), name='retrieve-survey'),
]

if settings.STORAGE_CLASS_NAME == 'local-storage':
    urlpatterns += [
        re_path(
            r'^media/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.MEDIA_ROOT}, name='media'
        ),
    ]
elif settings.STORAGE_CLASS_NAME == 'default':
    urlpatterns += [
        re_path(r'buyer/csv-dump/$', buyer.views.BuyerCSVDownloadAPIView.as_view(), name='buyer-csv-dump'),
        re_path(
            r'supplier/csv-dump/$', company.views.CompanyUserCSVDownloadAPIView.as_view(), name='supplier-csv-dump'
        ),
    ]


if settings.FEATURE_ENFORCE_STAFF_SSO_ENABLED:
    authbroker_urls = [
        re_path(
            r'^admin/login/$',
            RedirectView.as_view(
                url=reverse_lazy('authbroker_client:login'),
                query_string=True,
            ),
        ),
        re_path('^auth/', include('authbroker_client.urls')),
    ]

    urlpatterns = [re_path('^', include(authbroker_urls))] + urlpatterns

if settings.FEATURE_OPENAPI_ENABLED:
    urlpatterns += [
        path('openapi/', SpectacularAPIView.as_view(), name='schema'),
        path('openapi/ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('openapi/ui/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
