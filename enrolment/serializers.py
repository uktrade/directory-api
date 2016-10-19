from rest_framework import serializers

from enrolment import models


class EnrolmentSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)

    class Meta(object):
        model = models.Enrolment
        fields = (
            'aims',
            'company_number',
            'created',
            'company_email',
            'id',
            'personal_name',
        )
