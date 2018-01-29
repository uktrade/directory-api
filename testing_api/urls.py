from django.conf.urls import url

from testing_api.views import UserAPIView

urlpatterns = [
    url(
        r'^users/(?P<email>.*)/$',
        UserAPIView.as_view(),
        name="user-retrieve",),
]
