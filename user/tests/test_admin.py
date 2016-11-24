import pytest

from user.models import User
from user.tests import VALID_REQUEST_DATA as USER_DATA
from user.admin import export_users_to_csv
from company.models import Company
from company.tests import VALID_REQUEST_DATA as COMPANY_DATA


@pytest.mark.django_db
def test_csv_contains_all_expected_fields():
    company = Company.objects.create(**COMPANY_DATA)
    user = User(**USER_DATA)
    user.company = company
    user.save()

    csv_output = export_users_to_csv()

    csv_fields = ['id', 'sso_id', 'name', 'mobile_number',
                  'company_email', 'company_email_confirmed',
                  'company_email_confirmation_code', 'referrer',
                  'is_active', 'date_joined', 'terms_agreed',
                  'company_id', 'company_name', 'description',
                  'employees', 'export_status', 'keywords', 'logo',
                  'number', 'revenue', 'sectors', 'website',
                  'date_of_creation']
    user_values = [str(user.id), str(user.sso_id), user.name,
                   user.mobile_number, user.company_email,
                   str(user.company_email_confirmed),
                   user.company_email_confirmation_code, user.referrer,
                   str(user.is_active), "2017-03-21 13:12:00+00:00",
                   str(user.terms_agreed)]
    company_values = [str(company.id), company.name, company.description,
                      company.employees, company.export_status,
                      company.keywords, str(company.logo),
                      company.number, company.revenue, '',
                      company.website, company.date_of_creation]
    header = ','.join(csv_fields)
    line1 = ','.join(user_values + company_values)
    assert csv_output.getvalue() == header + '\r\n' + line1 + '\r\n'
