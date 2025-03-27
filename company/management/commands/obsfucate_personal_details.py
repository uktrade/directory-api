import argparse

from django.conf import settings
from django.core.management import BaseCommand

from company.models import CompanyUser


class Command(BaseCommand):

    START_INDEX = 1
    END_INDEX = -1
    MASK_CHAR = '*'

    count = 0

    @staticmethod
    def email_count():
        Command.count += 1
        return Command.count

    def mask_email_data(self, data):
        if not data:
            return data
        name = data.split('@')[0]
        address = data.split('@')[1]
        name = self.mask_string_data(name)
        address = self.mask_string_data(address)
        return f'{name}-{Command.email_count()}@{address}'

    def mask_string_data(self, data):
        if not data:
            return data
        ret = f'{data[:self.START_INDEX]}{self.MASK_CHAR * len(data[self.START_INDEX:self.END_INDEX])}{data[self.END_INDEX:]}'  # noqa:E501
        return ret

    def mask_json_data(self, data, fields):
        for field in fields:
            try:
                masked_field = self.mask_string_data(data[field])
                data[field] = masked_field
            except KeyError:
                pass
            else:
                data[field] = masked_field
        return data

    def mask_company_user(self, company_user, options):
        company_user.name = self.mask_string_data(company_user.name)
        company_user.mobile_number = self.mask_string_data(company_user.mobile_number)
        company_user.company_email = self.mask_email_data(company_user.company_email)

        if options['dry_run'] is False:
            company_user.save()

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry_run',
            action=argparse.BooleanOptionalAction,
            default=False,
            help='Show summary output only, do not update data',
        )

    def handle(self, *args, **options):  # noqa: C901

        if settings.APP_ENVIRONMENT.lower() == 'production':
            self.stdout.write(self.style.WARNING('Running in Production environment is disabled - exiting'))
            return

        # Obsfucate CompanyUser Data
        for companty_user in CompanyUser.objects.all():
            self.mask_company_user(companty_user, options)

        if options['dry_run'] is True:
            self.stdout.write(self.style.WARNING('Dry run -- no data updated.'))

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
