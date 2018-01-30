from rest_framework.serializers import (
    Serializer,
    CharField,
    BooleanField
)


class UserSerializer(Serializer):

    sso_id = CharField(max_length=200, read_only=True)
    is_verified = BooleanField(read_only=True)
