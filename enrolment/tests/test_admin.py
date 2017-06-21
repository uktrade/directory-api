import csv
import pytest
import io

from django.contrib.auth.models import User
from django.core.signing import Signer
from django.core.urlresolvers import reverse
from django.test import Client

from enrolment.models import TrustedSourceSignupCode


@pytest.fixture()
def superuser():
    return User.objects.create_superuser(
        username='admin', email='admin@example.com', password='test'
    )


@pytest.fixture()
def superuser_client(superuser):
    client = Client()
    client.force_login(superuser)
    return client


def build_csv_file(lineterminator):
    file_object = io.StringIO()
    writer = csv.writer(file_object, lineterminator=lineterminator)
    writer.writerow(['Company number', "Email"])
    writer.writerow(['11111111', 'fred@example.com'])
    writer.writerow(['11111112', 'jim@example.com'])
    file_object.seek(0)
    return file_object


@pytest.mark.django_db
@pytest.mark.parametrize('lineterminator', ['\n', '\r\n'])
def test_upload_enrolment_form_generates_csv(lineterminator, superuser_client):
    csv_file = build_csv_file(lineterminator=lineterminator)
    response = superuser_client.post(
        reverse('admin:generate_trusted_source_upload'),
        {'generated_for': 'COOL LTD', 'csv_file': csv_file}
    )

    assert response.status_code == 200

    code_one = TrustedSourceSignupCode.objects.get(company_number='11111111')
    code_two = TrustedSourceSignupCode.objects.get(company_number='11111112')

    buffer = io.StringIO(response.content.decode())
    reader = csv.reader(buffer)
    rows = list(reader)

    assert rows[0] == ['Company number', 'Email', 'Link']
    assert rows[1] == ['11111111', 'fred@example.com', code_one.enrolment_link]
    assert rows[2] == ['11111112', 'jim@example.com', code_two.enrolment_link]


@pytest.mark.django_db
def test_upload_enrolment_form_saves_code(superuser_client, superuser):
    csv_file = build_csv_file(lineterminator='\r\n')
    response = superuser_client.post(
        reverse('admin:generate_trusted_source_upload'),
        {'generated_for': 'COOL LTD', 'csv_file': csv_file}
    )

    assert response.status_code == 200
    assert TrustedSourceSignupCode.objects.count() == 2

    code_one = TrustedSourceSignupCode.objects.get(company_number='11111111')
    assert code_one.company_number == '11111111'
    assert code_one.email_address == 'fred@example.com'
    assert code_one.generated_for == 'COOL LTD'
    assert code_one.generated_by == superuser
    assert Signer().unsign(code_one.code) == 'fred@example.com'

    code_two = TrustedSourceSignupCode.objects.get(company_number='11111112')
    assert code_two.company_number == '11111112'
    assert code_two.email_address == 'jim@example.com'
    assert code_two.generated_for == 'COOL LTD'
    assert code_two.generated_by == superuser
    assert Signer().unsign(code_two.code) == 'jim@example.com'
