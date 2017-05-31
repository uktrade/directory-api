import json

from django.conf import settings
from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response

import enrolment.queue
from company.serializers import CompanySerializer

from enrolment.models import Enrolment
from enrolment import serializers
from supplier.serializers import SupplierSerializer


class EnrolmentCreateAPIView(CreateAPIView):

    model = Enrolment
    serializer_class = serializers.EnrolmentSerializer
    http_method_names = ("post", )

    def create(self, request, *args, **kwargs):
        """Sends valid request data to enrolment SQS queue"""
        serializer = self.get_serializer(data={
            'data': request.body
        })
        serializer.is_valid(raise_exception=True)

        if settings.SQS_ENROLMENT_QUEUE_ENABLED:
            enrolment.queue.EnrolmentQueue().send(
                data=json.dumps(request.data, ensure_ascii=False)
            )
            status_code = status.HTTP_202_ACCEPTED
        else:
            self.create_nested_objects(request.data)
            status_code = status.HTTP_201_CREATED

        return Response(
            data=serializer.data,
            status=status_code,
            headers=self.get_success_headers(serializer.data)
        )

    @transaction.atomic
    def create_nested_objects(self, data):
        try:
            company = self.create_company(
                export_status=data['export_status'],
                name=data['company_name'],
                number=data['company_number'],
                date_of_creation=data['date_of_creation'],
            )
            self.create_supplier(
                company=company,
                sso_id=data['sso_id'],
                company_email=data['company_email'],
            )
        except KeyError as error:
            raise ValidationError(
                'Missing key: "{key}"'.format(key=error)
            )

    @staticmethod
    def create_company(name, number, export_status, date_of_creation):
        serializer = CompanySerializer(data={
            'name': name,
            'number': number,
            'export_status': export_status,
            'date_of_creation': date_of_creation,
        })
        serializer.is_valid(raise_exception=True)
        return serializer.save()

    @staticmethod
    def create_supplier(sso_id, company_email, company):
        serializer = SupplierSerializer(data={
            'sso_id': sso_id,
            'company_email': company_email,
            'company': company.pk,
        })
        serializer.is_valid(raise_exception=True)
        return serializer.save()
