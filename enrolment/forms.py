import csv
import io
import json

from django import forms
from django.db import transaction

from enrolment import models


class PreVerifiedEnrolmentModelForm(forms.ModelForm):
    class Meta:
        model = models.PreVerifiedEnrolment
        fields = [
            'company_number',
            'company_name',
            'generated_for',
            'generated_by',
            'email_address',
        ]


class GeneratePreVerifiedCompanies(forms.Form):
    generated_for = forms.CharField(max_length=1000)
    csv_file = forms.FileField(
        help_text=('<a href="/admin/enrolment/preverifiedenrolment/example-template/">Download example csv file</a>')
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    @transaction.atomic
    def clean_csv_file(self):
        csv_file = io.TextIOWrapper(self.cleaned_data['csv_file'].file, encoding='utf-8')
        dialect = csv.Sniffer().sniff(csv_file.read(1024))
        csv_file.seek(0)
        reader = csv.reader(csv_file, dialect=dialect)
        next(reader, None)  # skip the headers
        row_errors = []
        for i, row in enumerate(reader):
            form = PreVerifiedEnrolmentModelForm(
                data={
                    'company_number': row[0],
                    'email_address': row[1],
                    'generated_for': self.cleaned_data['generated_for'],
                    'generated_by': self.user.pk,
                }
            )
            if not form.is_valid():
                row_errors.append(
                    '[Row {number}] {errors}'.format(
                        errors=json.dumps(form.errors),
                        number=i + 2,
                    )
                )
            else:
                form.save()
        if row_errors:
            raise forms.ValidationError(row_errors)
        return self.cleaned_data['csv_file']
