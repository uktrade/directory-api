from rest_framework import serializers

from enrollment import models


class EnrollmentSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)

    class Meta(object):
        model = models.Enrollment
        fields = ("id", "data",)
