import csv

from directory_constants import user_roles
from rest_framework.serializers import ValidationError

from django.db.models import BooleanField, Case, Count, When, Value
from django.utils.functional import cached_property

from company.models import Company
from supplier.models import Supplier


MESSAGE_ADMIN_NEEDED = 'A business profile must have at least one admin'


class SSOUser:
    def __init__(self, id, email, user_profile=None):
        self.id = id
        self.email = email
        self.user_profile = user_profile

    @property
    def pk(self):
        return self.id

    @property
    def full_name(self):
        if self.first_name and self.last_name:
            return f'{self.first_name} {self.last_name}'
        elif self.first_name:
            return self.first_name
        else:
            return ''

    @property
    def first_name(self):
        if self.user_profile and self.user_profile.get('first_name'):
            return self.user_profile['first_name']

    @property
    def last_name(self):
        if self.user_profile and self.user_profile.get('last_name'):
            return self.user_profile['last_name']

    @cached_property
    def supplier(self):
        try:
            return Supplier.objects.get(sso_id=self.id)
        except Supplier.DoesNotExist:
            return None


def generate_suppliers_csv(file_object, queryset):
    csv_excluded_fields = (
        'id',
        'company',
        'created',
        'modified',
        'company__collaboratorrequest',
        'company__company_type',
        'company__supplier_case_studies',
        'company__suppliers',
        'company__users',
        'company__verification_code',
        'company__messages',
        'supplieremailnotification',
        'company__ownershipinvite',
        'ownershipinvite',
        'company__collaboratorinvite',
        'collaboratorinvite',
        'collaborationinvite',
        'company__collaborationinvite',
    )
    fieldnames = [field.name for field in Supplier._meta.get_fields()
                  if field.name not in csv_excluded_fields]
    fieldnames += ['company__' + field.name
                   for field in Company._meta.get_fields()
                   if 'company__' + field.name
                   not in csv_excluded_fields]
    fieldnames.extend([
        'company__has_case_study',
        'company__number_of_case_studies'
    ])
    suppliers = queryset.select_related('company').all().annotate(
        company__has_case_study=Case(
            When(company__supplier_case_studies__isnull=False,
                 then=Value(True)
                 ),
            default=Value(False),
            output_field=BooleanField()
        ),
        company__number_of_case_studies=Count(
            'company__supplier_case_studies'
        ),
    ).values(*fieldnames)
    fieldnames.append('company__number_of_sectors')
    fieldnames = sorted(fieldnames)
    writer = csv.DictWriter(file_object, fieldnames=fieldnames)
    writer.writeheader()

    for supplier in suppliers:

        sectors = supplier.get('company__sectors')
        if sectors:
            supplier['company__number_of_sectors'] = len(sectors)
            supplier['company__sectors'] = ','.join(sectors)
        else:
            supplier['company__number_of_sectors'] = '0'
            supplier['company__sectors'] = ''

        writer.writerow(supplier)


def validate_other_admins_connected_to_company(company, sso_ids):
    # a company must have at least ope admin attached to it
    suppliers = company.suppliers.all()
    if suppliers.filter(role=user_roles.ADMIN).exclude(sso_id__in=sso_ids).count() == 0:
        raise ValidationError(MESSAGE_ADMIN_NEEDED)
