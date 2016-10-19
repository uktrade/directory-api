from rest_framework.generics import RetrieveUpdateAPIView

from user.serializers import UserSerializer
from user.models import User


class UserRetrieveUpdateAPIView(RetrieveUpdateAPIView):

    queryset = User.objects.all()
    serializer_class = UserSerializer
