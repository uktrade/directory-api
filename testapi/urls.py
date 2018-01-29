from django.conf.urls import url

from testapi.views import UserAPIView

urlpatterns = [
    url(
        r'^users/(?P<email>.*)/$',
        UserAPIView.as_view(),
        name="user-retrieve",),
]
