import boto3
import gzip

from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):

    key = 'flow/exports/staging/postcode_directory__latest/'

    def handle(self, *args, **options):
        """
            Download latest postcode file from s3
            unzip downloaded postcode file
            store latest postcode data in the database
        """
        if settings.FEATURE_USE_POSTCODES_FROM_S3:
            get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))
            s3 = boto3.client(
                's3',
                 aws_access_key_id=settings.AWS_ACCESS_KEY_ID_DATA_SERVICES,
                 aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_DATA_SERVICES,
                 region_name=settings.AWS_S3_REGION_NAME,
            )
            paginator = s3.get_paginator( "list_objects" )
            page_iterator = paginator.paginate( Bucket = settings.AWS_STORAGE_BUCKET_NAME_DATA_SERVICES, Prefix = self.key)
            for page in page_iterator:
                if "Contents" in page:
                    last_added = [obj['Key'] for obj in sorted( page["Contents"], key=get_last_modified)][-1]
                    if last_added:
                        with gzip.GzipFile(fileobj=last_added.get()["Body"]) as gzipfile:
                            postcodes_jsonl = gzipfile.read()
