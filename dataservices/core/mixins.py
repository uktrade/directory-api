from dataservices.management.commands.helpers import (
    get_s3_data_iterator,
    get_s3_file,
    read_jsonl_lines,
    save_s3_data_to_database,
    unzip_s3_gzip_file,
)


class S3DownloadMixin:

    def do_handle(self, prefix, save_func):
        """
        Download latest data file from s3
        unzip downloaded data file
        store latest data in the database
        """
        assert all([prefix, save_func])

        get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))  # noqa

        page_iterator = get_s3_data_iterator(prefix)

        for page in page_iterator:
            if "Contents" in page:
                last_added = [obj['Key'] for obj in sorted(page["Contents"], key=get_last_modified)][-1]
                if last_added:
                    s3_file = get_s3_file(last_added)
                    if s3_file:
                        body = s3_file.get('Body', None)
                        if body:
                            result_jsonl = unzip_s3_gzip_file(body)
                            if result_jsonl:
                                results = read_jsonl_lines(result_jsonl)
                                if results:
                                    save_s3_data_to_database(results, save_func)
