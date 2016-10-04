from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter
from registration.views import RegistrationViewSet


router = DefaultRouter()
router.register(r"registration", RegistrationViewSet, base_name="registration")

urlpatterns = [

    url(r"^", include(router.urls, namespace="drf")),

]
