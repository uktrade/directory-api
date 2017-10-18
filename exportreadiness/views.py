from rest_framework.generics import CreateAPIView, RetrieveAPIView, \
    get_object_or_404

from .models import TriageResult
from .serializers import TriageResultSerializer


class TriageResultCreateRetrieveView(CreateAPIView, RetrieveAPIView):
    serializer_class = TriageResultSerializer

    def get_object(self):
        return get_object_or_404(
            TriageResult.objects.all(),
            sso_id=self.request.user.id
        )

    def post(self, request, *args, **kwargs):
        pass
