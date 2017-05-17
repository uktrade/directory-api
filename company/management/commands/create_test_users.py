from django.core.management import BaseCommand

from company.models import Company
from user.models import User


class Command(BaseCommand):
    """Pass the sso_id create in directory-sso."""

    help = 'Used to create a supplier and company for integration tests.'

    def add_arguments(self, parser):
        parser.add_argument('sso_id', nargs='+', type=int)

    def handle(self, *args, **options):
        for sso_id in options['sso_id']:
            company = Company.objects.create(
                employees='1-10',
                export_status='ONE_TWO_YEARS_AGO',
                keywords='test',
                name='Test company {sso_id}'.format(sso_id=sso_id),
                is_published=True,
                verification_code='000000000000',
                verified_with_code=True,
                is_verification_letter_sent=True,
            )
            user = User.objects.create(sso_id=sso_id, company=company)

            self.stdout.write(
                self.style.SUCCESS('Successfully created user "%s"' % user.id)
            )
            self.stdout.write(
                self.style.SUCCESS('Successfully created '
                                   'company "%s"' % company.id)
            )
