from django.core.management.base import BaseCommand

from company.models import Company, CompanyUser
from company.tests.factories import CompanyFactory, CompanyUserFactory


class Command(BaseCommand):
    help = 'Masks personal company/supplier fields with test data'

    def handle(self, *args, **options):
        self.mask_company_data()
        self.mask_supplier_data()

    def mask_company_data(self):
        queryset = Company.objects.all()
        failed = 0
        succeded = 0
        for company in queryset:
            try:
                message = f'Company {company.pk} updated'
                company_factory = CompanyFactory.build()
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

    def mask_supplier_data(self):
        failed = 0
        succeded = 0
        for supplier in CompanyUser.objects.all():
            try:
                supplier_factory = CompanyUserFactory.build()
                message = f'supplier {supplier.pk} updated'
                supplier.name = supplier_factory.name
                supplier.company_email = supplier_factory.company_email
                supplier.mobile_number = supplier_factory.mobile_number
                supplier.save()
                self.stdout.write(self.style.SUCCESS(message))
                succeded += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(e))
                failed += 1
        self.stdout.write(self.style.SUCCESS(f'{succeded} supplier updated'))
        self.stdout.write(self.style.WARNING(f'{failed} supplier failed'))
