from datetime import datetime, timedelta

from freezegun import freeze_time

from django.utils import timezone

from company.tests.factories import CompanyFactory


@freeze_time()
def test_populate_company_populate_verification_date(migration):
    app = 'company'
    model_name = 'Company'
    name = '0037_auto_20170306_1154'
    migration.before(app, name).get_model(app, model_name)

    now = timezone.make_aware(datetime.utcnow()._date_to_freeze())
    company_three_date = now - timedelta(days=1)
    company_four_date = now - timedelta(days=2)

    company_one = CompanyFactory.create(
        verified_with_code=False,
        date_verification_letter_sent=None,
    )
    company_two = CompanyFactory.create(
        verified_with_code=True,
        date_verification_letter_sent=None
    )
    company_three = CompanyFactory.create(
        verified_with_code=False,
        date_verification_letter_sent=company_three_date,
    )
    company_four = CompanyFactory.create(
        verified_with_code=True,
        date_verification_letter_sent=company_four_date,
    )

    migration.apply('company', '0038_auto_20170306_1200')

    for company in [company_one, company_two, company_three, company_four]:
        company.refresh_from_db()

    # dates should not be updated
    assert company_one.date_verification_letter_sent is None
    assert company_three.date_verification_letter_sent == company_three_date
    assert company_four.date_verification_letter_sent == company_four_date
    # dates should be updated
    assert company_two.date_verification_letter_sent == now
