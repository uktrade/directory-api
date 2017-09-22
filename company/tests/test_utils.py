import datetime
from unittest import mock

import pytest
from django.utils import timezone
from freezegun import freeze_time

from company.tests import factories
from company import models, search, utils


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


@pytest.mark.django_db
@pytest.mark.rebuild_elasticsearch
def test_rebuild_and_populate_elasticsearch_index():
    published_company = factories.CompanyFactory(is_published=True)
    unpublished_company = factories.CompanyFactory(is_published=False)

    published_case_study = factories.CompanyCaseStudyFactory(
        company=published_company
    )
    unpublished_case_study = factories.CompanyCaseStudyFactory(
        company=unpublished_company
    )

    search.CompanyDocType.get(id=published_company.pk).delete()
    search.CaseStudyDocType.get(id=published_case_study.pk).delete()
    utils.rebuild_and_populate_elasticsearch_index(models.Company)

    assert search.CompanyDocType.get(id=published_company.pk) is not None
    assert search.CaseStudyDocType.get(id=published_case_study.pk) is not None

    assert search.CompanyDocType.get(
        id=unpublished_company.pk, ignore=404
    ) is None
    assert search.CaseStudyDocType.get(
        id=unpublished_case_study.pk, ignore=404
    ) is None
