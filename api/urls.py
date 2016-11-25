from django.conf.urls import url, include
from django.contrib import admin

from api.views import documentation, HealthCheckAPIView
from company.views import (
    CompanyCaseStudyViewSet,
    CompanyNumberValidatorAPIView,
    CompanyPublicProfileRetrieveAPIView,
    CompanyRetrieveUpdateAPIView,
)
from user.views import (
    UserRetrieveUpdateAPIView,
    ConfirmCompanyEmailAPIView,
    UserEmailValidatorAPIView,
    UserMobileNumberValidatorAPIView,
)
from enrolment.views import EnrolmentCreateAPIView, SendSMSVerificationAPIView
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
        r'enrolment/verification-sms/$',
        SendSMSVerificationAPIView.as_view(),
        name='verification-sms',
    ),
    url(
        r'user/(?P<sso_id>[0-9]+)/company/$',
        CompanyRetrieveUpdateAPIView.as_view(),
        name='company'
    ),
    url(
        r'^user/(?P<sso_id>[0-9]+)/company/case-study/$',
        CompanyCaseStudyViewSet.as_view({'post': 'create'}),
        name='company-case-study',
    ),
    url(
        r'^user/(?P<sso_id>[0-9]+)/company/case-study/(?P<pk>[0-9]+)/$',
        CompanyCaseStudyViewSet.as_view({
            'get': 'retrieve',
            'patch': 'partial_update',
            'delete': 'destroy',
        }),
        name='company-case-study-detail',
    ),
    url(
        r'user/(?P<sso_id>[0-9]+)/$',
        UserRetrieveUpdateAPIView.as_view(),
        name='user'
    ),
    url(
        r'company/public/(?P<companies_house_number>.*)/$',
        CompanyPublicProfileRetrieveAPIView.as_view(),
        name='company-public-profile'
    ),
    url(
        r'enrolment/confirm/$',
        ConfirmCompanyEmailAPIView.as_view(),
        name='confirm-company-email'
    ),
    url(
        r'validate/company-number/$',
        CompanyNumberValidatorAPIView.as_view(),
        name='validate-company-number'
    ),
    url(
        r'validate/email-address/$',
        UserEmailValidatorAPIView.as_view(),
        name='validate-email-address'
    ),
    url(
        r'validate/phone-number/$',
        UserMobileNumberValidatorAPIView.as_view(),
        name='validate-phone-number'
    ),
    url(
        r'buyer/$',
        BuyerCreateAPIView.as_view(),
        name='buyer-create',
    ),
]
