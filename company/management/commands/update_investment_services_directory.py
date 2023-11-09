"""
Management utility to update Investment Services Directory.
"""
import ast
import csv
from datetime import datetime

import requests
from django.core.management.base import BaseCommand, CommandError

from company.models import Company, CompanyCaseStudy, CompanyUser
from core.helpers import get_companies_house_profile


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

    def is_update(self, name: str) -> bool:
        if "update" in name:
            return True
        return False

    def model(self, name: str):
        if "company_" in name:
            return Company
        elif "casestudy_" in name:
            return CompanyCaseStudy
        return CompanyUser

    def get_app_number(self, row: dict) -> str:
        return row['app_number']

    def clean_values(self, row: dict) -> dict:
        for key, value in row.items():
            if type(value) == str:
                # convert bool
                if value == "TRUE":
                    row[key] = True
                elif value == "FALSE":
                    row[key] = False
                # strip and truncate to 1000 (max field length)
                else:
                    striped_value = value.strip()
                    truncated_value = (striped_value[:1000]) if len(striped_value) > 1000 else striped_value
                    row[key] = truncated_value
        return row

    def removed_unwanted_data_columns(self, row: dict) -> dict:
        try:
            row.pop("app_number")
        except KeyError:
            pass
        try:
            row.pop("??")
        except KeyError:
            pass
        return row

    def adjust_field_types(self, row: dict) -> dict:
        json_fields = [
            "expertise_products_services",
        ]
        lists = ["expertise_industries", "expertise_regions", "expertise_languages"]
        for key, value in row.items():
            if key in json_fields:
                test = ast.literal_eval(value)
                row[key] = test
            if key in lists:
                try:
                    row[key] = [v.strip() for v in ast.literal_eval(value)]
                except SyntaxError:
                    pass
        return row

    def fetch_companies_house_data(self, row: dict) -> dict:
        number = row["number"]
        try:
            profile = get_companies_house_profile(number)
            if profile.get('date_of_creation'):
                row["date_of_creation"] = datetime.strptime(profile['date_of_creation'], '%Y-%m-%d').date()
            if profile.get('registered_office_address'):
                address = profile['registered_office_address']
                row["address_line_1"] = address.get('address_line_1', '')
                row["address_line_2"] = address.get('address_line_2', '')
                row["locality"] = address.get('locality', '')
                row["po_box"] = address.get('po_box', '')
                row["postal_code"] = address.get('postal_code', '')
            if profile.get('sic_codes'):
                row["companies_house_sic_codes"] = profile.get('sic_codes', [])
            if profile.get('company_status'):
                row["companies_house_company_status"] = profile.get('company_status', '')
        except requests.exceptions.HTTPError:
            pass
        if "UNKNOWN" in number:
            row["number"] = None
        return row

    def handle(self, *args, **options):
        # Company supplied data
        source_files = {
            "company_update": "investment_supplier_data/company_update.csv",
            "companycasestudy_update": "investment_supplier_data/companycasestudy_update.csv",
            "companyuser_update": "investment_supplier_data/companyuser_update.csv",
            "company_add": "investment_supplier_data/company_add.csv",
            "companycasestudy_add": "investment_supplier_data/companycasestudy_add.csv",
            "companyuser_add": "investment_supplier_data/companyuser_add.csv",
        }

        # Validate each source file
        for key, source_file in source_files.items():
            self.validate_source_file(source_file)

        # Deactivate all case studies
        for company in Company.objects.filter(is_published_investment_support_directory=True):
            company.supplier_case_studies.all().update(is_published_case_study=False)

        # Variables to help process data in loop
        company_ids = []
        processed_companies = {}

        for key, source_file in source_files.items():
            _model = self.model(key)
            _is_update = self.is_update(key)
            try:
                with open(source_file, "r", encoding='utf-8') as csv_file:
                    csv_reader = csv.DictReader(
                        csv_file, quotechar='"', delimiter=',', quoting=csv.QUOTE_ALL, skipinitialspace=True
                    )
                    line_count = 0
                    for origin_row in csv_reader:
                        if line_count == 0:
                            line_count += 1
                        cleaned_row_values = self.clean_values(origin_row)
                        app_id = self.get_app_number(cleaned_row_values)
                        cleaned_row = self.removed_unwanted_data_columns(cleaned_row_values)

                        try:
                            # Update Company Data
                            if _is_update and _model == Company:
                                id = cleaned_row['id']
                                investment_company = Company.objects.filter(id=id)
                                if investment_company.exists():
                                    # This will update the object
                                    address_added = self.fetch_companies_house_data(cleaned_row)
                                    adjust_types = self.adjust_field_types(address_added)
                                    investment_company.update(**adjust_types)
                                    investment_company = investment_company.first()
                                    processed_companies[app_id] = {
                                        "company_obj": investment_company,
                                        "name": investment_company.name,
                                        "url": investment_company.public_profile_url,
                                        "email": investment_company.email_address,
                                    }
                                    company_ids.append(id)
                                else:
                                    # This will create a new object
                                    address_added = self.fetch_companies_house_data(cleaned_row)
                                    adjust_types = self.adjust_field_types(address_added)
                                    investment_company = Company.objects.create(**address_added)
                                    processed_companies[app_id] = {
                                        "company_obj": investment_company,
                                        "name": investment_company.name,
                                        "url": investment_company.public_profile_url,
                                        "email": investment_company.email_address,
                                    }
                                    company_ids.append(investment_company.id)

                            # Create new Company
                            if not _is_update and _model == Company:
                                # Sanity check - does the company exist?
                                number = cleaned_row['number']
                                investment_company = Company.objects.filter(number=number)
                                if investment_company.exists():
                                    # This will update the object
                                    address_added = self.fetch_companies_house_data(cleaned_row)
                                    adjust_types = self.adjust_field_types(address_added)
                                    investment_company.update(**adjust_types)
                                    investment_company = investment_company.first()
                                    processed_companies[app_id] = {
                                        "company_obj": investment_company,
                                        "name": investment_company.name,
                                        "url": investment_company.public_profile_url,
                                        "email": investment_company.email_address,
                                    }
                                    company_ids.append(investment_company.id)
                                else:
                                    # This will create a new object
                                    address_added = self.fetch_companies_house_data(cleaned_row)
                                    adjust_types = self.adjust_field_types(address_added)
                                    investment_company = Company.objects.create(**address_added)
                                    processed_companies[app_id] = {
                                        "company_obj": investment_company,
                                        "name": investment_company.name,
                                        "url": investment_company.public_profile_url,
                                        "email": investment_company.email_address,
                                    }
                                    company_ids.append(investment_company.id)

                            # Create new CompanyCaseStudy
                            if _is_update and _model == CompanyCaseStudy:
                                cleaned_row.update({"title": f"A Case Study By {processed_companies[app_id]['name']}"})
                                CompanyCaseStudy.objects.create(**cleaned_row)

                            # Create new CompanyCaseStudy for new Company
                            if not _is_update and _model == CompanyCaseStudy:
                                cleaned_row.update(
                                    {
                                        "title": f"A Case Study By {processed_companies[app_id]['name']}",
                                        "company_id": processed_companies[app_id]["company_obj"].id,
                                    }
                                )
                                CompanyCaseStudy.objects.create(**cleaned_row)

                            # Update CompanyUser
                            if _is_update and _model == CompanyUser:
                                company_id = cleaned_row['company_id']
                                company_email = cleaned_row['company_email']
                                user = CompanyUser.objects.filter(company_id=company_id, company_email=company_email)
                                if user.exists():
                                    user.update(**cleaned_row)
                                    company = user.first().company
                                    company.mobile_number = cleaned_row["mobile_number"]
                                    company.save()

                            # Create CompanyUser
                            if not _is_update and _model == CompanyUser:
                                pass

                        except KeyError:
                            pass
            except FileNotFoundError:
                raise CommandError(f"No such file or directory: '{source_file}'")

        # Remove all other companies from directory
        Company.objects.exclude(id__in=company_ids).update(is_published_investment_support_directory=False)

        # Add processed companies to directory
        Company.objects.filter(id__in=company_ids).update(is_published_investment_support_directory=True)

        # Remove company objects from dict
        for key, value in processed_companies.items():
            value.pop("company_obj")

        print(processed_companies)
        return ">>>Finished"
