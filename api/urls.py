from django.conf.urls import url, include
from django.contrib import admin

from api.views import documentation, HealthCheckAPIView
from company.views import (
    CompanyCaseStudyViewSet,
    CompanyNumberValidatorAPIView,
    CompanyPublicProfileViewSet,
    CompanySearchAPIView,
    CompanyRetrieveUpdateAPIView,
    PublicCaseStudyViewSet,
    VerifyCompanyWithCodeAPIView,
)
from notifications.views import (
    AnonymousUnsubscribeCreateAPIView
)
from supplier.views import (
    GeckoTotalRegisteredSuppliersView,
    SupplierRetrieveExternalAPIView,
    SupplierRetrieveUpdateAPIView,
    UnsubscribeSupplierAPIView,
)
from enrolment.views import EnrolmentCreateAPIView
from buyer.views import BuyerCreateAPIView
from contact.views import CreateMessageToSupplierAPIView

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
        r'^docs/$',
        documentation
    ),
    url(
        r'enrolment/$',
        EnrolmentCreateAPIView.as_view(),
        name='enrolment'
    ),
    url(
        r'supplier/(?P<sso_id>[0-9]+)/company/$',
        CompanyRetrieveUpdateAPIView.as_view(),
        name='company'
    ),
    url(
        r'supplier/(?P<sso_id>[0-9]+)/company/verify/$',
        VerifyCompanyWithCodeAPIView.as_view(),
        name='company-verify'
    ),
    url(
        r'^supplier/(?P<sso_id>[0-9]+)/company/case-study/$',
        CompanyCaseStudyViewSet.as_view({'post': 'create'}),
        name='company-case-study',
    ),
    url(
        r'^supplier/(?P<sso_id>[0-9]+)/company/case-study/(?P<pk>[0-9]+)/$',
        CompanyCaseStudyViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='company-case-study-detail',
    ),
    url(
        r'public/supplier/(?P<sso_id>[0-9]+)/$',
        SupplierRetrieveExternalAPIView.as_view(),
        name='public-protected-supplier-details'
    ),
    url(
        r'supplier/(?P<sso_id>[0-9]+)/$',
        SupplierRetrieveUpdateAPIView.as_view(),
        name='supplier'
    ),
    url(
        r'supplier/(?P<sso_id>[0-9]+)/unsubscribe/$',
        UnsubscribeSupplierAPIView.as_view(),
        name='unsubscribe-supplier'
    ),
    url(
        r'supplier/gecko/total-registered/$',
        GeckoTotalRegisteredSuppliersView.as_view(),
        name='gecko-total-registered-suppliers'
    ),
    url(
        r'public/case-study/(?P<pk>.*)/$',
        PublicCaseStudyViewSet.as_view({'get': 'retrieve'}),
        name='public-case-study-detail'
    ),
    url(
        r'public/company/(?P<companies_house_number>.*)/$',
        CompanyPublicProfileViewSet.as_view({'get': 'retrieve'}),
        name='company-public-profile-detail'
    ),
    url(
        r'public/company/$',
        CompanyPublicProfileViewSet.as_view({'get': 'list'}),
        name='company-public-profile-list'
    ),
    url(
        r'validate/company-number/$',
        CompanyNumberValidatorAPIView.as_view(),
        name='validate-company-number'
    ),
    url(
        r'buyer/$',
        BuyerCreateAPIView.as_view(),
        name='buyer-create',
    ),
    url(
        r'contact/supplier/$',
        CreateMessageToSupplierAPIView.as_view(),
        name='company-public-profile-contact-create'
    ),
    url(
        r'notifications/anonymous-unsubscribe/$',
        AnonymousUnsubscribeCreateAPIView.as_view(),
        name='anonymous-unsubscribe'
    ),
    url(
        r'company/search/$',
        CompanySearchAPIView.as_view(),
        name='company-search'
    ),

]

if settings.STORAGE_CLASS_NAME == 'local-storage':
    urlpatterns += [
        url(
            r'^media/(?P<path>.*)$',
            'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}
        ),
    ]
