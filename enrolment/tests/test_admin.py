import csv
import pytest
import io

from django.contrib.auth.models import User
from django.urls import reverse
from django.test import Client

from enrolment.models import PreVerifiedEnrolment


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


@pytest.fixture
def csv_invalid_rows():
    file_object = io.StringIO()
    writer = csv.writer(file_object)
    writer.writerow(['Company number', "Email"])
    writer.writerow(['11111111', 'fred@example.com'])
    writer.writerow(['11111112', 'jimATexample.com'])
    writer.writerow(['', 'jim@example.com'])
    writer.writerow(['11111111', 'fred@example.com'])
    file_object.seek(0)
    return file_object


@pytest.mark.django_db
def test_upload_enrolment_form_saves_verified(superuser_client, superuser):
    csv_file = build_csv_file(lineterminator='\r\n')
    response = superuser_client.post(
        reverse('admin:pre-verify-companies'),
        {'generated_for': 'COOL LTD', 'csv_file': csv_file}
    )

    assert response.status_code == 302
    assert PreVerifiedEnrolment.objects.count() == 2

    verified_one = PreVerifiedEnrolment.objects.get(company_number='11111111')
    assert verified_one.company_number == '11111111'
    assert verified_one.email_address == 'fred@example.com'
    assert verified_one.generated_for == 'COOL LTD'
    assert verified_one.generated_by == superuser

    verified_two = PreVerifiedEnrolment.objects.get(company_number='11111112')
    assert verified_two.company_number == '11111112'
    assert verified_two.email_address == 'jim@example.com'
    assert verified_two.generated_for == 'COOL LTD'
    assert verified_two.generated_by == superuser


@pytest.mark.django_db
def test_upload_enrolment_form_shows_erros(superuser_client, csv_invalid_rows):
    expected_error_one = (
         b'[Row 4] {&quot;company_number&quot;: '
         b'[&quot;This field is required.&quot;]}'
    )

    response = superuser_client.post(
        reverse('admin:pre-verify-companies'),
        {'generated_for': 'COOL LTD', 'csv_file': csv_invalid_rows}
    )

    assert response.status_code == 200
    assert expected_error_one in response.content


@pytest.mark.django_db
def test_upload_enrolment_form_rolls_back(superuser_client, csv_invalid_rows):
    # the first few rows were valid, but we dont want to save them - we want
    # to return the csv to the trade organisation with the validation errors,
    # and only when all rows are valid so we want to save them all
    response = superuser_client.post(
        reverse('admin:pre-verify-companies'),
        {'generated_for': 'COOL LTD', 'csv_file': csv_invalid_rows}
    )

    assert response.status_code == 200
    assert PreVerifiedEnrolment.objects.count() == 0


@pytest.mark.django_db
def test_download_preverified_template(superuser_client):
    response = superuser_client.get(reverse('admin:example-template'))

    assert response.content == (
        b'Company number,Email\r\n'
        b'90000001,comany@exmaple.com,'
        b'This is an example company. Delete this row.\r\n'
    )
    assert (
        response['Content-Disposition'] ==
        'attachment; filename="template.csv"'
    )
    assert response['content-type'] == 'text/csv'
