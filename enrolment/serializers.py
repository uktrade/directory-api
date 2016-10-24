from rest_framework import serializers

from django.db import transaction

from enrolment import models
from company.serializers import CompanySerializer
from user.serializers import UserSerializer


class EnrolmentSerializer(serializers.ModelSerializer):

    id = serializers.CharField(read_only=True)
    data = serializers.JSONField(binary=True)

    class Meta(object):
        model = models.Enrolment
        fields = (
            'created',
            'data',
            'id',
        )

    def create(self, validated_data):
        instance = super().create(validated_data)
        self.create_nested_objects(validated_data)
        return instance

    @transaction.atomic
    def create_nested_objects(self, validated_data):
        try:
            validated_company_data = {
                'aims': validated_data['data']['aims'],
                'number': validated_data['data']['company_number'],
            }
            validated_user_data = {
                'company_email': validated_data['data']['company_email'],
                'name': validated_data['data']['personal_name'],
                'referrer': validated_data['data']['referrer'],
            }
        except KeyError as error:
            raise serializers.ValidationError(
                'missing key: "{key}"'.format(key=error)
            )
        company = self.create_company(**validated_company_data)
        self.create_user(company=company, **validated_user_data)

    def create_company(self, aims, number):
        serializer = CompanySerializer(data={
            'aims': aims,
            'number': number,
        })
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def create_user(self, company_email, name, referrer, company):
        serializer = UserSerializer(data={
            'company_email': company_email,
            'name': name,
            'referrer': referrer,
            'company': company.pk,
        })
        serializer.is_valid(raise_exception=True)
        return serializer.save()
