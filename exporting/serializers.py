from rest_framework import serializers

from exporting import models


class OfficeSerializer(serializers.ModelSerializer):
    is_match = serializers.BooleanField()

    class Meta:
        model = models.Office
        fields = (
            'is_match',
            'region_id',
            'region_ids',
            'name',
            'address_street',
            'address_city',
            'address_postcode',
            'email',
            'phone',
            'phone_other',
            'phone_other_comment',
            'website',
            'override_office_details',
        )
