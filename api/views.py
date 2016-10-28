import json

from rest_framework import response, schemas, status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_swagger.renderers import OpenAPIRenderer, SwaggerUIRenderer


@api_view()
@renderer_classes([OpenAPIRenderer, SwaggerUIRenderer])
def documentation(request):
    generator = schemas.SchemaGenerator(title='Export Directory API')
    return response.Response(generator.get_schema(request=request))


class HealthCheckAPIView(APIView):

    permission_classes = ()
    http_method_names = ("get", )

    def get(self, request, *args, **kwargs):

        return Response(
            data=json.dumps({
                "status_code": status.HTTP_200_OK,
                "detail": "Hello world"
            }),
            status=status.HTTP_200_OK,
        )
