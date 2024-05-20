from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.generic import TemplateView
from rest_framework.views import APIView

from core.helpers import get_file_from_s3
from core.permissions import IsAuthenticatedCSVDump
from core.pingdom.services import health_check_services


class CSVDumpAPIView(APIView):
    permission_classes = [IsAuthenticatedCSVDump]
    bucket = None
    key = None
    filename = None

    def get(self, request, format=None):
        csv_file = get_file_from_s3(bucket=self.bucket, key=self.key)
        response = HttpResponse(csv_file['Body'].read(), content_type="text/csv")
        content = 'attachment; filename="{filename}"'.format(filename=self.filename)
        response['Content-Disposition'] = content
        return response


HEALTH_CHECK_STATUS = 0
HEALTH_CHECK_EXCEPTION = 1


class PingDomView(TemplateView):
    template_name = 'directory_healthcheck/pingdom.xml'

    status = 'OK'

    @method_decorator(never_cache)
    def get(self, *args, **kwargs):

        checked = {}
        for service in health_check_services:
            checked[service.name] = service().check()

        if all(item[HEALTH_CHECK_STATUS] for item in checked.values()):
            return HttpResponse(
                render_to_string(self.template_name, {'status': self.status, 'errors': []}),
                status=200,
                content_type='text/xml',
            )
        else:
            self.status = 'FALSE'
            errors = []
            for service_result in filter(lambda x: x[HEALTH_CHECK_STATUS] is False, checked.values()):
                errors.append(service_result[HEALTH_CHECK_EXCEPTION])
            return HttpResponse(
                render_to_string(self.template_name, {'status': self.status, 'errors': errors}),
                status=500,
                content_type='text/xml',
            )
