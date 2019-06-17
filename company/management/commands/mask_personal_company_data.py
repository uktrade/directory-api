from django.core.management.base import BaseCommand
from company.tests.factories import CompanyFactory

from company import models


class Command(BaseCommand):
    help = 'Masks personal company fields with test data'

    def handle(self, *args, **options):
        queryset = models.Company.objects.all()
        failed = 0
        succeded = 0
        for company in queryset:
            try:
                message = f'Company {company.pk} updated'
                company_factory = CompanyFactory()
                company.name = company_factory.name
                company.mobile_number = company_factory.mobile_number
                company.postal_full_name = company_factory.postal_full_name
                company.address_line_1 = company_factory.address_line_1
                company.address_line_2 = company_factory.address_line_2
                company.postal_code = company_factory.postal_code
                company.po_box = company_factory.po_box
                company.email_address = company_factory.email_address
                company.email_full_name = company_factory.email_full_name
                company.save()
                self.stdout.write(self.style.SUCCESS(message))
                succeded += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
                failed += 1
        self.stdout.write(self.style.SUCCESS(f'{succeded} companies updated'))
        self.stdout.write(self.style.WARNING(f'{failed} companies failed'))
