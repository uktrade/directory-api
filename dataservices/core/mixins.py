import io
import zlib

import boto3
import sqlalchemy as sa
from django.conf import settings
from pg_bulk_ingest import to_file_like_obj
from sqlalchemy.ext.declarative import declarative_base


def unzip_s3_gzip_file(file_body, max_bytes):
    dobj = zlib.decompressobj(max_bytes)
    for chunk in file_body:
        uncompressed_chunk = dobj.decompress(chunk)
        if uncompressed_chunk:
            yield uncompressed_chunk
        elif dobj.eof:
            unused = dobj.unused_data
            dobj = zlib.decompressobj(max_bytes)
            uncompressed_chunk = dobj.decompress(unused)
            if uncompressed_chunk:
                yield uncompressed_chunk

    uncompressed_chunk = dobj.flush()
    if uncompressed_chunk:
        yield uncompressed_chunk


def _get_s3_client_kwargs():
    kwargs = {}
    if hasattr(settings, 'AWS_ACCESS_KEY_ID_DATA_SERVICES') and hasattr(settings, 'AWS_SECRET_ACCESS_KEY_DATA_SERVICES'):
        kwargs['aws_access_key_id'] = settings.AWS_ACCESS_KEY_ID_DATA_SERVICES
        kwargs['aws_secret_access_key'] = settings.AWS_SECRET_ACCESS_KEY_DATA_SERVICES

    return kwargs


def get_s3_paginator(prefix):

    s3 = boto3.client(
        's3',
        region_name=settings.AWS_S3_REGION_NAME,
        **_get_s3_client_kwargs(),
    )

    return s3.get_paginator('list_objects').paginate(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME_DATA_SERVICES, Prefix=prefix
    )


def get_s3_file(key):
    s3 = boto3.client(
        's3',
        region_name=settings.AWS_S3_REGION_NAME,
        **_get_s3_client_kwargs(),
    )

    response = s3.get_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME_DATA_SERVICES,
        Key=key,
    )
    return response


class S3DownloadMixin:

    def delete_temp_tables(self, table_names):
        Base = declarative_base()
        metadata = sa.MetaData()
        engine = sa.create_engine(settings.DATABASE_URL, future=True)
        metadata.reflect(bind=engine)
        for name in table_names:
            table = metadata.tables.get(name, None)
            if table is not None:
                Base.metadata.drop_all(engine, [table], checkfirst=True)

    def do_handle(self, prefix):
        """
        Download latest data file from s3
        unzip downloaded data file
        store latest data in the database
        params:
            prefix: str - Bucket Path on the Dataservices s3 bucket.
        """
        assert None not in [prefix]

        page_iterator = get_s3_paginator(prefix)
        files = []
        for page in page_iterator:
            if "Contents" in page:
                for obj in page['Contents']:
                    this_page = obj['Key']
                    this_last_modified_date = obj['LastModified']
                    files.append((this_page, this_last_modified_date))

        if files:
            last_added = sorted(files, key=lambda x: x[1])[-1][0]
            s3_file = get_s3_file(last_added)
            if s3_file:
                body = s3_file.get('Body', None)
                if body:
                    chunks = unzip_s3_gzip_file(body, (32 + zlib.MAX_WBITS))
                    text_lines = io.TextIOWrapper(to_file_like_obj(chunks), encoding="utf-8", newline="")
                    if text_lines:
                        return text_lines
                    else:
                        return None
