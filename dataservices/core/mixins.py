import io

from dataservices.management.commands.helpers import (
    get_s3_file,
    get_s3_paginator,
    read_jsonl_lines,
    to_file_like_obj,
    unzip_s3_gzip_file,
)


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
        assert all([prefix, save_func])

        get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))  # noqa

        page_iterator = get_s3_paginator(prefix)
        last_modified = None
        for page in page_iterator:
            if "Contents" in page:
                this_page = [obj['Key'] for obj in sorted(page["Contents"], key=get_last_modified)][-1]
                this_modified_date = [obj['LastModified'] for obj in sorted(page["Contents"], key=get_last_modified)][
                    -1
                ]
                if not last_modified:
                    last_added = this_page
                elif this_modified_date > last_modified:
                    last_added = this_page
                last_modified = this_modified_date

        if last_added:
            s3_file = get_s3_file(last_added)
            if s3_file:
                body = s3_file.get('Body', None)
                breakpoint()
                if body:
                    chunks = unzip_s3_gzip_file(body)
                    text_lines = io.TextIOWrapper(to_file_like_obj(chunks), encoding="utf-8", newline="")
                    if text_lines:
                        results = read_jsonl_lines(text_lines)
                        if results:
                            save_func(results)
