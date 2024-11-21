import io
import zlib

from pg_bulk_ingest import to_file_like_obj

from dataservices.management.commands.helpers import get_s3_file, get_s3_paginator, read_jsonl_lines, unzip_s3_gzip_file


class S3DownloadMixin:

    def do_handle(self, prefix, save_func):
        """
        Download latest data file from s3
        unzip downloaded data file
        store latest data in the database
        params:
            prefix: str - Bucket Path on the Dataservices s3 bucket.
            save_func: method - Method that saves the <data> param to the database.
        """
        assert None not in [prefix, save_func]

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
                        results = read_jsonl_lines(text_lines)
                        if results:
                            save_func(results)
