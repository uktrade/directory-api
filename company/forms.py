import csv
import io
import json

from directory_components.fields import PaddedCharField

from django import forms
from django.db import transaction

from company import helpers, models


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
        if not value:
            value = None
        elif not value.startswith('http'):
            value = f'https://{value}'
        return value


class SocialURLField(forms.URLField):
    empty_values = forms.URLField.empty_values + ['N/A', 'n/a']

    def to_python(self, value):
        value = super().to_python(value)
        if not value:
            return None
        if ' ' in value:
            return None
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
            'email_address',
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
        ]
        field_classes = {
            'number': CompanyNumberField,
            'website': CompanyUrlField,
            'facebook_url': FacebookURLField,
            'twitter_url': TwitterURLField,
            'linkedin_url': LinkedInURLField,
        }


def company_type_parser(company_number):
    if company_number:
        return models.Company.COMPANIES_HOUSE
    return models.Company.SOLE_TRADER


class EnrolCompanies(forms.Form):
    csv_file = forms.FileField()

    @transaction.atomic
    def clean_csv_file(self):
        self.companies = []
        csv_file = io.TextIOWrapper(
            self.cleaned_data['csv_file'].file, encoding='utf-8'
        )
        dialect = csv.Sniffer().sniff(csv_file.read(1024))
        csv_file.seek(0)
        reader = csv.reader(csv_file, dialect=dialect)
        next(reader, None)  # skip the headers
        row_errors = []
        for i, row in enumerate(reader):
            address = helpers.AddressParser(row[2])
            form = CompanyModelForm(data={
                'address_line_1': address.line_1,
                'address_line_2': address.line_2,
                'company_type': company_type_parser(row[8]),
                'country': 'UK',
                'email_address': row[4],
                'email_full_name': row[3],
                'facebook_url': row[11],
                'is_exporting_services': True,
                'keywords': row[14],
                'linkedin_url': row[12],
                'mobile_number': row[5],
                'name': row[1],
                'number': row[8],
                'po_box': address.po_box,
                'postal_code': address.postal_code,
                'postal_full_name': row[3],
                'twitter_url': row[10],
                'verified_with_preverified_enrolment': True,
                'website': row[9],
            })

            if form.is_valid():
                self.companies.append(form.save())
            else:
                row_errors.append('[Row {number}] {errors}'.format(
                    errors=json.dumps(form.errors),
                    number=i+2,
                ))
        if row_errors:
            raise forms.ValidationError(row_errors)
        return self.cleaned_data['csv_file']
