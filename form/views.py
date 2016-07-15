from rest_framework.viewsets import ModelViewSet

from .serializers import FormSerializer
from .models import Form


class FormViewSet(ModelViewSet):

    model = Form
    serializer_class = FormSerializer
    http_method_names = ("post",)
