"""
Management utility to update Investment Services Directory.
"""
import csv

from django.core.management.base import BaseCommand, CommandError
from django.db import DEFAULT_DB_ALIAS

from company.models import Company


class Command(BaseCommand):
    help = "Management utility to update Investment Services Directory"
    requires_migrations_checks = True
    stealth_options = ("stdin",)

    def validate_source_file(self, source_file):
        try:
            source_file_type = source_file.split(".")[-1]
            if source_file_type.lower() != "csv":
                raise CommandError(f"Source file must be 'csv': '{source_file}'")
            return source_file
        except IndexError:
            raise CommandError(f"Please provide the source_file path (csv only): '{source_file}'")

    def handle(self, *args, **options):
        source_file = input("Path to CSV file:")

        source_file = self.validate_source_file(source_file)

        companies = Company.objects.all()
        investment_companies = companies.filter(is_published_investment_support_directory=True)

        print(f'>>> Companies in DB: {companies.count()}')
        print(f'>>> Investment companies before updates: {investment_companies.count()}')

        company_ids = []
        company_ids_not_found = []
        companies_updated = 0
        companies_not_found = 0

        try:
            with open(source_file, "r", encoding='utf-8') as csv_file:
                csv_reader = csv.DictReader(csv_file)
                line_count = 0
                for row in csv_reader:
                    if line_count == 0:
                        line_count += 1
                    try:
                        # for key, value in row.items():
                        #     key[value] = value.strip()
                        striped_id = row['number'].strip()
                        investment_company = companies.filter(number=striped_id)
                        if investment_company.exists():
                            # This will update the object
                            # investment_company.update(**row)

                            company_ids.append(striped_id)
                            companies_updated += 1
                        else:
                            company_ids_not_found.append(striped_id)
                            companies_not_found += 1
                    except KeyError:
                        pass
        except FileNotFoundError:
            raise CommandError(f"No such file or directory: '{source_file}'")

        companies = companies.exclude(number__in=company_ids + company_ids_not_found)
        for company in companies:
            company.is_published_investment_support_directory = False
            ##Commit change
            # company.save()

        print(f'>>> Companies being removed from directory: {companies.count()}')
        print(f'>>> Companies updated: {companies_updated}')
        print(f'>>> Companies not found: {companies_not_found}')
        if companies_not_found:
            print('>>> Companies not found:')
            print(company_ids_not_found)
        return ">>> Finished"
