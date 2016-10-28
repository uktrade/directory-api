from django.conf.urls import url

from api.views import documentation, HealthCheckAPIView
from company.views import (
    CompaniesHouseProfileDetailsAPIView,
    CompanyNumberValidatorAPIView,
    CompanyRetrieveUpdateAPIView,
)
from user.views import UserRetrieveUpdateAPIView, ConfirmCompanyEmailAPIView
from enrolment.views import EnrolmentCreateAPIView, SendSMSVerificationAPIView

urlpatterns = [
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
        r'company/details/(?P<sso_user_id>[0-9]+)/$',
        CompanyRetrieveUpdateAPIView.as_view(),
        name='company'
    ),
    url(
        r'user/(?P<sso_id>[0-9]+)/$',
        UserRetrieveUpdateAPIView.as_view(),
        name='user'
    ),
    url(
        r'confirm-company-email/$',
        ConfirmCompanyEmailAPIView.as_view(),
        name='confirm-company-email'
    ),
    url(
        r'validate-company-number/$',
        CompanyNumberValidatorAPIView.as_view(),
        name='validate-company-number'
    ),
    url(
        r'company/companies-house-profile/$',
        CompaniesHouseProfileDetailsAPIView.as_view(),
        name='companies-house-profile',
    ),

]
