from django.core.management import BaseCommand

from company import models


class Command(BaseCommand):
    """Pass the sso_id created in directory-sso."""

    help = 'Used to create a supplier and company for integration tests.'

    def add_arguments(self, parser):
        parser.add_argument('sso_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for sso_id in options['sso_id']:
            company = models.Company.objects.create(
                employees='1-10',
                export_status='ONE_TWO_YEARS_AGO',
                has_exported_before=True,
                keywords='test',
                name='Test company {sso_id}'.format(sso_id=sso_id),
                is_published_investment_support_directory=True,
                is_published_find_a_supplier=True,
                verification_code='000000000000',
                verified_with_code=True,
                is_verification_letter_sent=True,
            )
            user = models.CompanyUser.objects.create(sso_id=sso_id, company=company)

            self.stdout.write(self.style.SUCCESS('Successfully created user "%s"' % user.id))
            self.stdout.write(self.style.SUCCESS('Successfully created company "%s"' % company.id))
