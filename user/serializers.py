from rest_framework import serializers

from .models import OwnershipInvite


class OwnershipInviteSerializer(serializers.ModelSerializer):

    class Meta:
        model = OwnershipInvite
        fields = (
            'new_owner_email',
            'company',
            'requestor',
        )
