from rest_framework.renderers import JSONRenderer


class CustomDataMetadataJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        view = renderer_context.get('view')
        metadata = view.get_serializer().get_metadata()
        response_data = {}

        if isinstance(data, list):
            data = data[: view.limit]

        if metadata:
            response_data['metadata'] = metadata

        if renderer_context["response"].status_code == 200:
            response_data['data'] = data
        else:
            response_data = data

        return super().render(response_data, accepted_media_type, renderer_context)
