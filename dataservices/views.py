from rest_framework.generics import RetrieveAPIView

from dataservices import serializers, models
from rest_framework.response import Response
from django.http import Http404


class RetrieveEaseOfBusinessIndex(RetrieveAPIView):
    serializer_class = serializers.EaseOfDoingBusinessSerializer
    permission_classes = []
    lookup_url_kwarg = 'country_code'
    lookup_field = 'country_code__iexact'
    queryset = models.EaseOfDoingBusiness.objects.all()

    def get(self, *args, **kwargs):
        try:
            return super().get(self, *args, **kwargs)
        except Http404:
            return Response(data={})


class RetrieveCorruptionPerceptionsIndex(RetrieveAPIView):
    serializer_class = serializers.CorruptionPerceptionsIndexSerializer
    permission_classes = []
    lookup_url_kwarg = 'country_code'
    lookup_field = 'country_code__iexact'
    queryset = models.CorruptionPerceptionsIndex.objects.all()

    def get(self, *args, **kwargs):
        try:
            return super().get(self, *args, **kwargs)
        except Http404:
            return Response(data={})
