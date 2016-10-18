from rest_framework.generics import RetrieveUpdateAPIView

from user.serializers import UserSerializer
from user.models import User


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    model = User
    queryset = model.objects
    serializer_class = UserSerializer
