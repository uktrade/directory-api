import io
import zlib
from datetime import datetime

import boto3
import sqlalchemy as sa
from django.conf import settings
from pg_bulk_ingest import to_file_like_obj
from sqlalchemy.ext.declarative import declarative_base

from dataservices.models import DBTIngestionHistory

DATA_FIELD = 0
DATA_FILE_NAME_FIELD = 1


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


def get_s3_paginator(prefix):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID_DATA_SERVICES,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_DATA_SERVICES,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    return s3.get_paginator('list_objects').paginate(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME_DATA_SERVICES, Prefix=prefix
    )


def store_ingestion_data(file_names, import_name):
    for file_name in file_names:
        DBTIngestionHistory(
            import_name=import_name,
            imported_file=file_name,
            imported_when=datetime.now(),
            import_status=True,
        ).save()


def get_s3_file(key):
    s3 = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID_DATA_SERVICES,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY_DATA_SERVICES,
        region_name=settings.AWS_S3_REGION_NAME,
    )
    response = s3.get_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME_DATA_SERVICES,
        Key=key,
    )
    return response


class S3DownloadMixin:

    def get_ingested_files_for_import(self, import_name):
        return list(
            DBTIngestionHistory.objects.filter(import_name=import_name, import_status=True).values_list('imported_file')
        )

    def get_all_files_not_ingested(self, files, import_name):
        ingested_files = self.get_ingested_files_for_import(import_name)
        return [file for file in files if file not in ingested_files]

    def delete_temp_tables(self, table_names):
        Base = declarative_base()
        metadata = sa.MetaData()
        engine = sa.create_engine(settings.DATABASE_URL, future=True)
        metadata.reflect(bind=engine)
        for name in table_names:
            table = metadata.tables.get(name, None)
            if table is not None:
                Base.metadata.drop_all(engine, [table], checkfirst=True)

    def return_data(self, last_added):
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

    def do_handle(self, prefix, multiple_files=False, import_name=None):
        """
        Download latest data file from s3
        unzip downloaded data file
        params:
            prefix: str - Bucket Path on the Dataservices s3 bucket.
        return:
            text_lines - TextWrapper for files
            last_added - last added file or files
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

        if files and not multiple_files:
            last_added = sorted(files, key=lambda x: x[DATA_FILE_NAME_FIELD])[-1][DATA_FIELD]
            return self.return_data(last_added), last_added
        elif files:
            files = self.get_all_files_not_ingested(files, import_name)
            all_files = []
            for file in files:
                data = self.return_data(file[DATA_FIELD])
                if data:
                    all_files.append(
                        {
                            'file': data,
                        }
                    )

            return all_files, files
        else:
            return None, None
