from rest_framework import serializers

from .models import Form


class FormSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)

    class Meta(object):
        model = Form
        fields = ("id", "data",)
