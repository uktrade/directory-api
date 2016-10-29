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
                'export_status': validated_data['data']['export_status'],
                'name': validated_data['data']['company_name'],
                'number': validated_data['data']['company_number'],
            }
            validated_user_data = {
                'sso_id': validated_data['data']['sso_id'],
                'company_email': validated_data['data']['company_email'],
                'mobile_number': validated_data['data']['mobile_number'],
                'referrer': validated_data['data']['referrer'],
            }
        except KeyError as error:
            raise serializers.ValidationError(
                'missing key: "{key}"'.format(key=error)
            )
        company = self.create_company(**validated_company_data)
        self.create_user(company=company, **validated_user_data)

    def create_company(self, name, number, export_status):
        serializer = CompanySerializer(data={
            'name': name,
            'number': number,
            'export_status': export_status,
        })
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    def create_user(
            self, sso_id, company_email, mobile_number, referrer, company):
        serializer = UserSerializer(data={
            'sso_id': sso_id,
            'company_email': company_email,
            'referrer': referrer,
            'mobile_number': mobile_number,
            'company': company.pk,
        })
        serializer.is_valid(raise_exception=True)
        return serializer.save()


class SMSVerificationSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=20)
