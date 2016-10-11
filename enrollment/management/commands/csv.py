import csv
import datetime
import json
import io

from django.core.management.base import BaseCommand

from enrollment import models


class Command(BaseCommand):

    def handle(self, *args, **options):
        live_date = datetime.date(year=2016, month=7, day=21)
        enrollments = models.Enrollment.objects.filter(
            created__gte=live_date
        ).order_by('created')

        enrollment_dicts = []
        keys = set()

        for enrollment in enrollments:
            enrollment_dict = {'created': enrollment.created}
            enrollment_dict = json.loads(enrollment.data)
            enrollment_dict.update(enrollment)
            enrollment_dicts.append(enrollment_dict)
            keys.update(set(enrollment.keys()))

        stringio = io.StringIO()
        headers = ['created'] + sorted(keys)
        csv_writer = csv.DictWriter(stringio, headers)
        csv_writer.writeheader()

        for enrollment_dict in enrollment_dicts:
            csv_writer.writerow(enrollment_dict)
        return stringio.getvalue()
