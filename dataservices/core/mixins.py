from dataservices.management.commands.helpers import (
    get_s3_data_iterator,
    read_jsonl_lines,
    save_s3_data_to_database,
    unzip_s3_gzip_file,
)


class S3DownloadMixin:

    def do_handle(self, prefix, s3_fields, model_class_name):
        """
        Download latest data file from s3
        unzip downloaded data file
        store latest data in the database
        """
        self.prefix = prefix
        self.s3_fields = s3_fields
        self.model_class_name = model_class_name

        assert all(
            [
                self.prefix,
                self.s3_fields,
                self.model_class_name,
            ]
        )

        get_last_modified = lambda obj: int(obj['LastModified'].strftime('%s'))  # noqa
        page_iterator = get_s3_data_iterator(self.prefix)
        breakpoint()
        for page in page_iterator:
            if "Contents" in page:
                last_added = [obj['Key'] for obj in sorted(page["Contents"], key=get_last_modified)][-1]
                if last_added:
                    result_jsonl = unzip_s3_gzip_file(last_added.get()["Body"])
                    if result_jsonl:
                        results = read_jsonl_lines(result_jsonl)
                        if results:
                            save_s3_data_to_database(results, self.s3_fields, self.model_class_name)
