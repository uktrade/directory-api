import csv
import io
import json
import re
from difflib import SequenceMatcher

from directory_components.fields import PaddedCharField

from django import forms
from django.db import transaction

from company import constants, helpers, models
from enrolment.forms import PreVerifiedEnrolmentModelForm
from directory_constants import expertise


class MobileNumberField(forms.CharField):
    def to_python(self, value):
        # assume to be a list of numbers, not a single number
        value = super().to_python(value)
        if len(value) > self.max_length:
            value = ''
        return value


class CompanyNumberField(PaddedCharField):

    def __init__(self, fillchar='0', *args, **kwargs):
        super().__init__(fillchar=fillchar, *args, **kwargs)

    def to_python(self, value):
        value = super().to_python(value)
        if value:
            if 'n/a' in value.lower() or 'there is no' in value.lower():
                return None
            value = value.replace(' ', '')
        else:
            value = None
        return value


class CompanyUrlField(forms.URLField):
    def to_python(self, value):
        value = super().to_python(value)
        # handle multiple websites - pick the first
        value = re.split(r' and |\n', value)[0]
        # remove comments in brackets
        value = re.sub(r'\(.*\)', '', value)
        # assume to be a common on the website, not a website
        if '.' not in value:
            value = ''
        return value.strip() or ''


class SocialURLField(forms.URLField):
    empty_values = forms.URLField.empty_values + ['N/A', 'n/a']

    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return ''
        if ' ' in value:
            return ''
        if not value.startswith(self.website):
            # may be at "at tag"
            value = value.replace('@', '')
            # may be a non-https facebook link, so just get the last component
            value = value.split('/')[-1]
            value = f'{self.website}{value}'
        return value


class FacebookURLField(SocialURLField):
    website = 'https://www.facebook.com/'


class TwitterURLField(SocialURLField):
    website = 'https://www.twitter.com/'


class LinkedInURLField(SocialURLField):
    website = 'https://www.linkedin.com/company/'


class CompanyModelForm(forms.ModelForm):
    class Meta:
        model = models.Company
        fields = [
            'address_line_1',
            'address_line_2',
            'name',
            'number',
            'company_type',
            'country',
            'has_exported_before',
            'locality',
            'po_box',
            'postal_code',
            'website',
            'keywords',
            'twitter_url',
            'facebook_url',
            'linkedin_url',
            'verified_with_preverified_enrolment',
            'is_exporting_services',
            'mobile_number',
            'is_uk_isd_company',
            'expertise_products_services',
        ]
        field_classes = {
            'number': CompanyNumberField,
            'website': CompanyUrlField,
            'facebook_url': FacebookURLField,
            'twitter_url': TwitterURLField,
            'linkedin_url': LinkedInURLField,
            'mobile_number': MobileNumberField,
        }


def company_type_parser(company_number):
    if company_number:
        if CompanyNumberField(max_length=8).to_python(company_number):
            return models.Company.COMPANIES_HOUSE
    return models.Company.SOLE_TRADER


class EnrolCompanies(forms.Form):
    generated_for = forms.ChoiceField(
        choices=(
            (constants.UK_ISD, 'UK ISD'),
        ),
    )
    csv_file = forms.FileField()

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    @transaction.atomic
    def clean_csv_file(self):
        self.created_companies = []
        self.skipped_companies = []
        csv_file = io.TextIOWrapper(
            self.cleaned_data['csv_file'].file, encoding='utf-8'
        )
        dialect = csv.Sniffer().sniff(csv_file.read(1024))
        csv_file.seek(0)
        reader = csv.reader(csv_file, dialect=dialect)
        next(reader, None)  # skip the headers
        errors = []
        for i, row in enumerate(reader):
            company_type = company_type_parser(row[8])
            is_uk_isd_company = (
                self.cleaned_data['generated_for'] == constants.UK_ISD
            )
            data = {
                'company_type': company_type,
                'facebook_url': row[11],
                'is_exporting_services': True,
                'keywords': row[14],
                'linkedin_url': row[12],
                'mobile_number': row[5],
                'name': row[1],
                'number': row[8],
                'postal_full_name': row[3],
                'twitter_url': row[10],
                'verified_with_preverified_enrolment': True,
                'website': row[9],
                'is_uk_isd_company': is_uk_isd_company,
            }
            if company_type == models.Company.SOLE_TRADER:
                address = helpers.AddressParser(row[2])
                data.update({
                    'address_line_1': address.line_1,
                    'address_line_2': address.line_2,
                    'country': 'UK',
                    'po_box': address.po_box,
                    'postal_code': address.postal_code,
                })

            form = CompanyModelForm(data=data)
            if form.is_valid():
                form.save()
                self.created_companies.append({
                    'name': form.instance.name,
                    'number': form.instance.number,
                    'email_address': row[4],
                })
                pre_verified_form = PreVerifiedEnrolmentModelForm(data={
                    'generated_for': self.cleaned_data['generated_for'],
                    'generated_by': self.user.pk,
                    'company_number': form.instance.number,
                })
                assert pre_verified_form.is_valid
                pre_verified_form.save()
            else:
                if 'number' in form.errors:
                    company = models.Company.objects.get(
                        number=form.instance.number
                    )
                    company.is_uk_isd_company = is_uk_isd_company
                    company.save()

                    self.skipped_companies.append({
                        'name': row[1],
                        'email_address': row[4],
                    })
                else:
                    self.add_bulk_errors(
                        errors=errors, row_number=i+2, line_errors=form.errors,
                    )
        if errors:
            raise forms.ValidationError(errors)
        return self.cleaned_data['csv_file']

    @staticmethod
    def add_bulk_errors(errors, row_number, line_errors):
        errors.append('[Row {number}] {errors}'.format(
            errors=json.dumps(line_errors),
            number=row_number,
        ))


class UploadExpertise(forms.Form):

    MSG_PRODUCT_SERVICE_NOT_FOUND = (
        'Unable to find following products & services'
    )
    MSG_COMPANY_NOT_FOUND = 'Company not found'
    MSG_COMPANY_TOO_MANY = 'More then one company returned'

    csv_file = forms.FileField()

    update_errors = []
    updated_companies = []

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    @transaction.atomic
    def clean_csv_file(self):

        csv_file = io.TextIOWrapper(
            self.cleaned_data['csv_file'].file, encoding='utf-8'
        )
        dialect = csv.Sniffer().sniff(csv_file.read(1024))
        csv_file.seek(0)
        reader = csv.reader(csv_file, dialect=dialect)
        next(reader, None)  # skip the headers

        for i, row in enumerate(reader):
            data = {
                'name': row[1],
                'number': row[8],
            }

            if data['number']:
                companies = models.Company.objects.filter(number=data['number'])
            else:
                companies = models.Company.objects.filter(name=data['name'])

            if companies.count() == 0:
                self.add_bulk_errors(
                    errors=self.update_errors,
                    row_number=i,
                    line_errors=self.MSG_COMPANY_NOT_FOUND),
            elif companies.count() > 1:
                self.add_bulk_errors(
                    errors=self.update_errors,
                    row_number=i,
                    line_errors=self.MSG_COMPANY_TOO_MANY,
                )
            else:
                company = companies[0]
                company.expertise_products_services = (
                    self.parse_products_services(
                        errors=self.update_errors,
                        row_number=i,
                        expertise_row=row[15]
                    )
                )
                company.save()
                self.updated_companies.append(company)

    def parse_products_services(self, errors, row_number, expertise_row):
        expertise_list = [x.strip() for x in expertise_row.split(',')]
        expertise_dict = {
            'Finance': expertise.FINANCIAL,
            'Management Consulting': expertise.MANAGEMENT_CONSULTING,
            'Human Resources': expertise.HUMAN_RESOURCES,
            'Legal': expertise.LEGAL,
            'Publicity': expertise.PUBLICITY,
            'Business Support': expertise.BUSINESS_SUPPORT
        }
        expertise_list_not_found = []
        parsed_expertise = {}
        for e in expertise_list:
            for key, values in expertise_dict.items():

                expertise_match = self.match_sequence(e, values)
                if expertise_match is not None:
                    if parsed_expertise.get(key):
                        parsed_expertise[key].append(expertise_match)
                        break
                    else:
                        parsed_expertise[key] = [expertise_match]
                        break
            else:
                expertise_list_not_found.append(e)

        if expertise_list_not_found:
            error_message = self.MSG_PRODUCT_SERVICE_NOT_FOUND + ' {}'.format(
                expertise_list_not_found
            )

            self.add_bulk_errors(
                errors=errors,
                row_number=row_number,
                line_errors=error_message,
            )
        return parsed_expertise

    @staticmethod
    def match_sequence(match_value, sequence_list):
        for v in sequence_list:
            match = SequenceMatcher(None, match_value.lower(), v.lower())
            if match.ratio() > 0.9:
                return v
        return None

    @staticmethod
    def add_bulk_errors(errors, row_number, line_errors):
        errors.append('[Row {number}] {errors}'.format(
            errors=json.dumps(line_errors),
            number=row_number,
        ))
