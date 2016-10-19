from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView

import oauth2_provider.views
import rest_auth.views
import rest_auth.registration.views

from enrolment.views import EnrolmentCreateAPIView
from company.views import CompanyRetrieveUpdateAPIView
from user.views import UserRetrieveUpdateAPIView
from api.views import documentation


admin.autodiscover()


rest_auth_patterns = [
    url(
        r'^registration/$',
        rest_auth.registration.views.RegisterView.as_view(),
        name='rest_register'
    ),

    # TODO: override this view to handle it and send post to /verify-email/
    # endpoint with proper key (see allauth.account.views.ConfirmEmailView for
    # example)
    url(
        r'^account-confirm-email/(?P<key>[-:\w]+)/$',
        TemplateView.as_view(),
        name='account_confirm_email'
    ),
    url(
        r'^registration/verify_email/$',
        rest_auth.registration.views.VerifyEmailView.as_view(),
        name='rest_verify_email'
    ),
    url(
        r'^user/$',
        rest_auth.views.UserDetailsView.as_view(),
        name='rest_user_details'
    ),
    url(
        r'^login/$',
        rest_auth.views.LoginView.as_view(),
        name='rest_login'
    ),
    url(
        r'^logout/$',
        rest_auth.views.LogoutView.as_view(),
        name='rest_logout'
    ),
    url(
        r'^password/reset/$',
        rest_auth.views.PasswordResetView.as_view(),
        name='rest_password_reset'
    ),
    url(
        r'^password/reset/confirm/$',
        rest_auth.views.PasswordResetConfirmView.as_view(),
        name='rest_password_reset_confirm'
    ),
    url(
        r'^password/change/$',
        rest_auth.views.PasswordChangeView.as_view(),
        name='rest_password_change'
    ),
]

oauth2_provider_patterns = [
    url(
        r'^authorize/$',
        oauth2_provider.views.AuthorizationView.as_view(),
        name="authorize"
    ),
    url(
        r'^token/$',
        oauth2_provider.views.TokenView.as_view(),
        name="token"
    ),
    url(
        r'^revoke_token/$',
        oauth2_provider.views.RevokeTokenView.as_view(),
        name="revoke-token"
    ),

    # Application management views
    url(
        r'^applications/$',
        oauth2_provider.views.ApplicationList.as_view(),
        name="list"
    ),
    url(
        r'^applications/register/$',
        oauth2_provider.views.ApplicationRegistration.as_view(),
        name="register"
    ),
    url(
        r'^applications/(?P<pk>\d+)/$',
        oauth2_provider.views.ApplicationDetail.as_view(),
        name="detail"
    ),
    url(
        r'^applications/(?P<pk>\d+)/delete/$',
        oauth2_provider.views.ApplicationDelete.as_view(),
        name="delete"
    ),
    url(
        r'^applications/(?P<pk>\d+)/update/$',
        oauth2_provider.views.ApplicationUpdate.as_view(),
        name="update"
    ),
    url(
        r'^authorized_tokens/$',
        oauth2_provider.views.AuthorizedTokensListView.as_view(),
        name="authorized-token-list"
    ),
    url(
        r'^authorized_tokens/(?P<pk>\d+)/delete/$',
        oauth2_provider.views.AuthorizedTokenDeleteView.as_view(),
        name="authorized-token-delete"
    ),
]

urlpatterns = [
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
        r'company/(?P<pk>[0-9]+)/$',
        CompanyRetrieveUpdateAPIView.as_view(),
        name='company'
    ),
    url(
        r'user/(?P<pk>[0-9]+)/$',
        UserRetrieveUpdateAPIView.as_view(),
        name='user'
    ),
    url(
        r'^auth/private/',
        include(rest_auth_patterns, namespace='rest_auth')
    ),
    url(
        r'^auth/public/',
        include(oauth2_provider_patterns, namespace='oauth2_provider')
    ),
]
