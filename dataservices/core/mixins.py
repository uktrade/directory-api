from dataservices.management.commands.helpers import (
    get_s3_data_iterator,
    get_s3_file,
    read_jsonl_lines,
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

        page_iterator = get_s3_data_iterator(prefix)
        last_added = None
        for page in page_iterator:
            if "Contents" in page:
                last_added_for_page = [obj['Key'] for obj in sorted(page["Contents"], key=get_last_modified)][-1]
                if not last_added:
                    last_added = last_added_for_page
                elif last_added_for_page['LastModified'] > last_added['LastModified']:
                    last_added = last_added_for_page

        if last_added:
            s3_file = get_s3_file(last_added)
            if s3_file:
                body = s3_file.get('Body', None)
                if body:
                    result_jsonl = unzip_s3_gzip_file(body)
                    if result_jsonl:
                        results = read_jsonl_lines(result_jsonl)
                        if results:
                            save_func(results)
