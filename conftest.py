import http
from unittest.mock import patch

import requests_mock
import requests

from company import helpers


def pytest_runtest_setup(item):
    company_profile = {
        'company_status': 'active',
        'date_of_creation': '2000-10-10',
    }

    companies_house_adapter = requests_mock.Adapter()
    companies_house_adapter.register_uri(
        'GET',
        helpers.company_profile_url.format(number='01234567'),
        json=company_profile,
        status_code=http.client.OK,
    )

    helpers.companies_house_session.mount(
        'https://api.companieshouse.gov.uk',
        companies_house_adapter
    )
