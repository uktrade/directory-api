from django.conf.urls import url, include
from django.contrib import admin

from api.views import documentation, HealthCheckAPIView
from company.views import (
    CompaniesHouseProfileDetailsAPIView,
    CompanyNumberValidatorAPIView,
    CompanyRetrieveUpdateAPIView,
)
from user.views import UserRetrieveUpdateAPIView, ConfirmCompanyEmailAPIView
from enrolment.views import EnrolmentCreateAPIView


admin.autodiscover()

urlpatterns = [
    url(
        r'^$',
        HealthCheckAPIView.as_view(),
        name='health-check'
    ),

    url(
        r'^admin/',
        include(admin.site.urls)
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
        r'company/details/(?P<pk>[0-9]+)/$',
        CompanyRetrieveUpdateAPIView.as_view(),
        name='company'
    ),
    url(
        r'user/(?P<pk>[0-9]+)/$',
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
    )


]
