import csv
import datetime
import json
import io

from django.core.management.base import BaseCommand

from registration import models


class Command(BaseCommand):

    def handle(self, *args, **options):
        live_date = datetime.date(year=2016, month=7, day=21)
        registrations = models.Registration.objects.filter(
            created__gte=live_date
        ).order_by('created')

        registration_dicts = []
        keys = set()

        for registration in registrations:
            registration_dict = {'created': registration.created}
            registration_dict = json.loads(registration.data)
            registration_dict.update(registration)
            registration_dicts.append(registration_dict)
            keys.update(set(registration.keys()))

        stringio = io.StringIO()
        headers = ['created'] + sorted(keys)
        csv_writer = csv.DictWriter(stringio, headers)
        csv_writer.writeheader()

        for registration_dict in registration_dicts:
            csv_writer.writerow(registration_dict)
        return stringio.getvalue()
