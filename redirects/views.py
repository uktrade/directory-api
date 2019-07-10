from rest_framework.views import APIView
from rest_framework.response import Response

from redirects import models, serializers
from django.http import HttpResponseNotFound


class RetrieveRedirect(APIView):

    permission_classes = []

    def get(self, request, *args, **kwargs):
        serializer_class = serializers.RedirectSerializer
        source_url = '/'+kwargs['key']+'/'
        try:
            obj = models.Redirect.objects.filter(source_url=source_url)
            resp = serializer_class(obj.first()).data
            resp.status_code = 404
            return Response(resp)
        except BaseException:
            raise HttpResponseNotFound
