from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, JsonResponse
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from company.models import Company
from company.serializers import CompanySerializer


class CacheView(GenericAPIView):
    '''
    Temporary view to help develop and test caching

    This view is only wired up to a url if settings.DEBUG == True
    '''

    permission_classes = []
    authentication_classes = []
    serializer_class = CompanySerializer

    def get_queryset(self):
        return Company.objects.all()

    def get_object(self):
        return self.get_queryset().last()

    def get(self, request):
        data = {}
        try:
            user = self.get_object()
            serializer = self.get_serializer(user)
            data = serializer.data
        except ObjectDoesNotExist:
            pass
        return JsonResponse(status=200, data=data)
