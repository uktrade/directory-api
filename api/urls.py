from django.conf.urls import url, include
from django.contrib import admin

from api.views import documentation, HealthCheckAPIView
from company.views import (
    CompanyCaseStudyViewSet,
    CompanyNumberValidatorAPIView,
    CompanyPublicProfileViewSet,
    CompanyRetrieveUpdateAPIView,
    VerifyCompanyWithCodeAPIView,
)
from supplier.views import (
    SupplierRetrieveUpdateAPIView,
    GeckoTotalRegisteredSuppliersView,
)
from enrolment.views import EnrolmentCreateAPIView
from buyer.views import BuyerCreateAPIView


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
        r'^company/case-study/$',
        CompanyCaseStudyViewSet.as_view({'post': 'create'}),
        name='company-case-study',
    ),
    url(
        r'^company/case-study/(?P<pk>[0-9]+)/$',
        CompanyCaseStudyViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='company-case-study-detail',
    ),
    url(
        r'supplier/(?P<sso_id>[0-9]+)/$',
        SupplierRetrieveUpdateAPIView.as_view(),
        name='supplier'
    ),
    url(
        r'supplier/gecko/total-registered/$',
        GeckoTotalRegisteredSuppliersView.as_view(),
        name='gecko-total-registered-suppliers'
    ),
    url(
        r'company/public/(?P<companies_house_number>.*)/$',
        CompanyPublicProfileViewSet.as_view({'get': 'retrieve'}),
        name='company-public-profile-detail'
    ),
    url(
        r'company/public/$',
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
]
