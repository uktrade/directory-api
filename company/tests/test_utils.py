import datetime
from unittest import mock

import pytest
from django.utils import timezone
from freezegun import freeze_time

from company.tests import factories
from company import utils


@pytest.mark.django_db
@freeze_time()
@mock.patch('company.utils.stannp_client')
def test_send_letter(mock_stannp_client):
    company = factories.CompanyFactory(verification_code='test')
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
