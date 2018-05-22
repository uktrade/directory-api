from django.http import JsonResponse
from django.views import View


class ActivityStreamView(View):
    def get(self, request, *args, **kwargs):
        return JsonResponse({})
