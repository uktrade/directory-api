import pytest

from user.models import User
from user.tests import VALID_REQUEST_DATA as USER_DATA
from user.admin import export_users_to_csv
from company.models import Company
from company.tests import VALID_REQUEST_DATA as COMPANY_DATA


EXPECTED_CSV_FIELDS = [
    'id', 'sso_id', 'name', 'mobile_number', 'company_email',
    'company_email_confirmed', 'company_email_confirmation_code',
    'referrer', 'is_active', 'date_joined', 'terms_agreed',
    'company_id', 'company_name', 'description', 'employees',
    'export_status', 'keywords', 'logo', 'number', 'revenue', 'sectors',
    'website', 'date_of_creation']


@pytest.fixture
def company():
    # fill in optional fields as well
    # TODO: logo should not be None. See ED-489
    kwargs = {'employees': '50', 'keywords': 'a,b,c',
              'logo': None, 'sectors': '[1,2,3]'}
    kwargs.update(COMPANY_DATA)
    return Company.objects.create(**kwargs)


@pytest.fixture
def user(company):
    # fill in optional fields
    kwargs = {
        'name': 'James Bond',
        'company_email_confirmation_code': 'ABCDEFG',
        'company': company,
    }
    kwargs.update(USER_DATA)
    return User.objects.create(**kwargs)


@pytest.mark.django_db
def test_csv_correctly_exported_when_some_fields_empty():
    # not all fields are filled in so checking correct handling of
    # None and empty string is being done
    company = Company.objects.create(**COMPANY_DATA)
    user = User.objects.create(company=company, **USER_DATA)
    # creating a company that should not be in the csv as is not
    # attached to a user
    Company.objects.create(number="01234568")

    csv_output = export_users_to_csv()

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
    header = ','.join(EXPECTED_CSV_FIELDS)
    line1 = ','.join(user_values + company_values)
    assert csv_output.getvalue() == header + '\r\n' + line1 + '\r\n'


@pytest.mark.django_db
def test_csv_correctly_exported_with_all_fields_filled_in(company, user):
    # TODO: company.logo should not be None but currently is. See ED-489

    csv_output = export_users_to_csv()

    user_values = [str(user.id), str(user.sso_id), user.name,
                   user.mobile_number, user.company_email,
                   str(user.company_email_confirmed),
                   user.company_email_confirmation_code, user.referrer,
                   str(user.is_active), "2017-03-21 13:12:00+00:00",
                   str(user.terms_agreed)]
    company_values = [str(company.id), company.name, company.description,
                      company.employees, company.export_status,
                      '"a,b,c"', str(company.logo),
                      company.number, company.revenue, '"[1,2,3]"',
                      company.website, str(company.date_of_creation)]
    header = ','.join(EXPECTED_CSV_FIELDS)
    line1 = ','.join(user_values + company_values)
    assert csv_output.getvalue() == header + '\r\n' + line1 + '\r\n'


@pytest.mark.django_db
def test_csv_export_handles_multiple_users():
    company1 = Company.objects.create(**COMPANY_DATA)
    company2 = Company.objects.create(number="01234568")
    user_data2 = {"sso_id": 2, "company_email": "2@example.com"}
    user_data3 = {"sso_id": 3, "company_email": "3@example.com",
                  "mobile_number": "07505605134"}
    User.objects.bulk_create([
        User(company=company1, **USER_DATA),
        User(company=company2, **user_data2),
        User(company=company2, **user_data3),
    ])

    csv_output = export_users_to_csv()

    csv_text = csv_output.getvalue()
    csv_lines = csv_text.split('\r\n')
    expected_header = ','.join(EXPECTED_CSV_FIELDS)
    assert len(csv_lines) == 5
    assert csv_lines[0] == expected_header
    assert csv_lines[4] == ''  # split leaves the last element as ''
    assert 'gargoyle@example.com' in csv_text  # user1 is there
    assert '2@example.com' in csv_text  # user2 is there
    assert '3@example.com' in csv_text  # user3 is there


@pytest.mark.django_db
def test_csv_export_handles_user_with_no_company():
    user = User.objects.create(company=None, **USER_DATA)

    csv_output = export_users_to_csv()

    user_values = [str(user.id), str(user.sso_id), user.name,
                   user.mobile_number, user.company_email,
                   str(user.company_email_confirmed),
                   user.company_email_confirmation_code, user.referrer,
                   str(user.is_active), "2017-03-21 13:12:00+00:00",
                   str(user.terms_agreed)]
    header = ','.join(EXPECTED_CSV_FIELDS)
    line1 = ','.join(user_values) + (12 * ',')  # empty company fields
    assert csv_output.getvalue() == header + '\r\n' + line1 + '\r\n'
