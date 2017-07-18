from django.core.management import BaseCommand

from company.models import Company


class Command(BaseCommand):

    help = 'Used to create a company for integration tests.'

    def add_arguments(self, parser):
        parser.add_argument('company_number', nargs='+', type=str)

    def handle(self, *args, **options):
        for company_number in options['company_number']:
            company = Company.objects.create(
                employees='1-10',
                export_status='ONE_TWO_YEARS_AGO',
                has_exported_before=True,
                keywords='test',
                name='Test company',
                is_published=True,
                verification_code='000000000000',
                verified_with_code=True,
                is_verification_letter_sent=True,
                number=company_number
            )

            self.stdout.write(
                self.style.SUCCESS('Successfully created '
                                   'company "%s"' % company.id)
            )
