from django.conf.urls import url, include

from rest_framework.routers import DefaultRouter
from form.views import FormViewSet

router = DefaultRouter()
router.register(r"form", FormViewSet, base_name="form")

urlpatterns = [

    url(r"^", include(router.urls, namespace="drf")),

]
