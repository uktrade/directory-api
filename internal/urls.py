from django.conf.urls import url

from internal.views import UserAPIView

urlpatterns = [
    url(
        r'^user/(?P<email>.*)/$',
        UserAPIView.as_view(),
        name="user-retrieve",),
]