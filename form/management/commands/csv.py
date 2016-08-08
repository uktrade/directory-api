import csv
import json
import io

from django.core.management.base import BaseCommand

from form.models import Form


class Command(BaseCommand):

    def handle(self, *args, **options):
        forms = Form.objects.all().order_by('created')
        form_dicts = []
        keys = set()
        for form in forms:
            form_dict = {'created': form.created}
            form_data = json.loads(form.data)
            form_dict.update(form_data)
            form_dicts.append(form_dict)
            keys.update(set(form_data.keys()))
        stringio = io.StringIO()
        headers = ['created'] + sorted(keys)
        csv_writer = csv.DictWriter(stringio, headers)
        csv_writer.writeheader()
        for form_dict in form_dicts:
            csv_writer.writerow(form_dict)
        return stringio.getvalue()
