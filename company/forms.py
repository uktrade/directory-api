import csv
import io
import json
import re

from directory_components.fields import PaddedCharField

from django import forms
from django.db import transaction

from company import constants, helpers, models
from enrolment.forms import PreVerifiedEnrolmentModelForm


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
            address = helpers.AddressParser(row[2])
            form = CompanyModelForm(data={
                'address_line_1': address.line_1,
                'address_line_2': address.line_2,
                'company_type': company_type_parser(row[8]),
                'country': 'UK',
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
                'is_uk_isd_company': (
                    self.cleaned_data['generated_for'] == constants.UK_ISD
                )
            })
            if form.is_valid():
                company = form.save()
                self.created_companies.append({
                    'name': row[1],
                    'number': company.number,
                    'email_address': row[4],
                })
                pre_verified_form = PreVerifiedEnrolmentModelForm(data={
                    'generated_for': self.cleaned_data['generated_for'],
                    'generated_by': self.user.pk,
                    'company_number': company.number,
                })
                assert pre_verified_form.is_valid
                pre_verified_form.save()
            else:
                if 'number' in form.errors:
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
