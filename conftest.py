import http
import re

import requests_mock

from company import helpers


def pytest_runtest_setup(item):
    company_profile = {
        'company_status': 'active',
        'date_of_creation': '2000-10-10',
    }

    companies_house_adapter = requests_mock.Adapter()
    companies_house_adapter.register_uri(
        'GET',
        re.compile('https://api.companieshouse.gov.uk/company/.*'),
        json=company_profile,
        status_code=http.client.OK,
    )

    helpers.companies_house_session.mount(
        'https://api.companieshouse.gov.uk',
        companies_house_adapter
    )
