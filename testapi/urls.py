from django.conf.urls import url

from testapi.views import UserAPIView

urlpatterns = [
    url(
        r'^user-by-email/(?P<email>.*)/$',
        UserAPIView.as_view(),
        name="user-retrieve",),
]
