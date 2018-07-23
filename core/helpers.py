import csv

import boto3
from ipware.ip2 import get_client_ip

from django.conf import settings
from django.db import models
from django_extensions.db.fields import (
    CreationDateTimeField, ModificationDateTimeField,
)
from django.http import HttpResponse
from django.utils.translation import ugettext_lazy as _

from core.constants import IP_RETRIEVER_NAME_GOV_UK, IP_RETRIEVER_NAME_IPWARE


class IpwareRemoteIPAddressRetriver:
    MESSAGE_NOT_FOUND = 'IP not found'
    MESSAGE_UNROUTABLE = 'IP is private'

    @classmethod
    def get_ip_address(cls, request):
        client_ip, is_routable = get_client_ip(request)
        if not client_ip:
            raise LookupError(cls.MESSAGE_NOT_FOUND)
        if not is_routable:
            raise LookupError(cls.MESSAGE_UNROUTABLE)
        return client_ip


class GovukPaaSRemoteIPAddressRetriver:
    MESSAGE_MISSING_HEADER = 'X-Forwarded-For not in HTTP headers'
    MESSAGE_INVALID_IP_COUNT = 'Not enough IP addresses in X-Forwarded-For'

    @classmethod
    def get_ip_address(cls, request):
        """
        Returns the IP of the client making a HTTP request, using the
        second-to-last IP address in the X-Forwarded-For header. This
        should not be able to be spoofed in GovukPaaS, but it is not
        safe to use in other environments.

        Args:
            request (HttpRequest): the incoming Django request object

        Returns:
            str: The IP address of the incoming request

        Raises:
            LookupError: The X-Forwarded-For header is not present, or
            does not contain enough IPs
        """
        if 'HTTP_X_FORWARDED_FOR' not in request.META:
            raise LookupError(cls.MESSAGE_MISSING_HEADER)

        x_forwarded_for = request.META['HTTP_X_FORWARDED_FOR']
        ip_addesses = x_forwarded_for.split(',')
        if len(ip_addesses) < 2:
            raise LookupError(cls.MESSAGE_INVALID_IP_COUNT)

        return ip_addesses[-2].strip()


class RemoteIPAddressRetriver:
    """
    Different environments retrieve the remote IP address differently. This
    class negotiates that.

    """

    @classmethod
    def __new__(cls, *args, **kwargs):
        if settings.REMOTE_IP_ADDRESS_RETRIEVER == IP_RETRIEVER_NAME_GOV_UK:
            return GovukPaaSRemoteIPAddressRetriver()
        elif settings.REMOTE_IP_ADDRESS_RETRIEVER == IP_RETRIEVER_NAME_IPWARE:
            return IpwareRemoteIPAddressRetriver()
        raise NotImplementedError()


def upload_file_object_to_s3(file_object, bucket, key):
    s3 = boto3.client('s3')
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=file_object.getvalue()
    )


def get_file_from_s3(bucket, key):
    s3 = boto3.client('s3',)
    file_object = s3.get_object(
        Bucket=bucket,
        Key=key
    )
    return file_object


def generate_csv_response(queryset, filename, excluded_fields):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = (
        'attachment; filename="{filename}"'.format(
            filename=filename
        )
    )
    generate_csv(
        file_object=response,
        queryset=queryset,
        excluded_fields=excluded_fields
    )
    return response


def generate_csv(file_object, queryset, excluded_fields):
    model = queryset.model
    fieldnames = sorted(
        [field.name for field in model._meta.get_fields()
         if field.name not in excluded_fields]
    )

    objects = queryset.all().values(*fieldnames)
    writer = csv.DictWriter(file_object, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(objects)

    return writer


class TimeStampedModel(models.Model):
    """Modified version of django_extensions.db.models.TimeStampedModel

    Unfortunately, because null=True needed to be added to create and
    modified fields, inheritance causes issues with field clash.

    """
    created = CreationDateTimeField(_('created'), null=True)
    modified = ModificationDateTimeField(_('modified'), null=True)

    def save(self, **kwargs):
        self.update_modified = kwargs.pop(
            'update_modified', getattr(self, 'update_modified', True))
        super(TimeStampedModel, self).save(**kwargs)

    class Meta:
        get_latest_by = 'modified'
        ordering = ('-modified', '-created',)
        abstract = True
