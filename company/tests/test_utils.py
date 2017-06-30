import datetime
from unittest import mock

import pytest
from django.utils import timezone
from freezegun import freeze_time

from company.tests.factories import CompanyFactory
from company import models, utils


@pytest.mark.django_db
@freeze_time()
@mock.patch('company.utils.stannp_client')
def test_send_letter(mock_stannp_client):
    company = CompanyFactory(verification_code='test')
    utils.send_verification_letter(company)
    mock_stannp_client.send_letter.assert_called_with(
        recipient={
            'postal_full_name': company.postal_full_name,
            'address_line_1': company.address_line_1,
            'address_line_2': company.address_line_2,
            'locality': company.locality,
            'country': company.country,
            'postal_code': company.postal_code,
            'po_box': company.po_box,
            'custom_fields': [
                ('full_name', company.postal_full_name),
                ('company_name', company.name),
                ('verification_code', company.verification_code),
                ('date', datetime.date.today().strftime('%d/%m/%Y')),
                ('company', company.name)
            ]
        },
        template='debug'
    )
    company.refresh_from_db()
    assert company.is_verification_letter_sent
    assert company.date_verification_letter_sent == timezone.now()


@pytest.mark.django_db
@mock.patch.object(utils, 'Index')
def test_populate_elasticsearch(mock_index):
    CompanyFactory.create()

    utils.populate_elasticsearch(models.Company)

    mock_index.assert_called_with('companies')
    assert mock_index().delete.call_count == 1
    assert mock_index().create.call_count == 1
