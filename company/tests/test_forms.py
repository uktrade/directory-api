import pytest
from directory_constants import company_types

from company import forms


@pytest.mark.parametrize(
    'value,expected',
    (
        ('', ''),
        (None, ''),
        ('very long ' * 100, ''),
    ),
)
def test_mobile_number_clean(value, expected):
    field = forms.MobileNumberField(max_length=100)
    assert field.to_python(value) == expected


@pytest.mark.parametrize(
    'value,expected',
    (
        ('11536552', '11536552'),
        ('6872466', '06872466'),
        ('OC404310', 'OC404310'),
        ('OC 321831', 'OC321831'),
        ('THERE IS NO IN ENGLAND ', None),
        ('0452 5852', '04525852'),
        ('N/A', None),
        ('N/a', None),
        ('n/a', None),
        (None, None),
        ('', None),
    ),
)
def test_company_number_clean(value, expected):
    field = forms.CompanyNumberField(max_length=8)
    assert field.to_python(value) == expected


@pytest.mark.parametrize(
    'value,expected',
    (
        ('www.example.com', 'http://www.example.com'),
        ('https://www.example.co.uk', 'https://www.example.co.uk'),
        (None, ''),
        ('', ''),
        ('www.example.com (pending)', 'http://www.example.com'),
        ('www.example.com and thing.com', 'http://www.example.com'),
        ('www.example.com\nthing.com', 'http://www.example.com'),
        ('in progress', ''),
    ),
)
def test_company_url_clean(value, expected):
    field = forms.CompanyUrlField()
    assert field.to_python(value) == expected


@pytest.mark.parametrize(
    'value,expected',
    (
        ('Foo bar on facebook', ''),
        ('www.facebook.com/example', 'https://www.facebook.com/example'),
        ('example', 'https://www.facebook.com/example'),
        ('@example', 'https://www.facebook.com/example'),
        ('https://www.facebook.com/example', 'https://www.facebook.com/example'),
        ('', ''),
        (None, ''),
    ),
)
def test_facebook_url_clean(value, expected):
    field = forms.FacebookURLField()
    assert field.to_python(value) == expected


@pytest.mark.parametrize(
    'value,expected',
    (
        ('Foo bar on twitter', ''),
        ('www.twitter.com/example', 'https://www.twitter.com/example'),
        ('example', 'https://www.twitter.com/example'),
        ('@example', 'https://www.twitter.com/example'),
        ('https://www.twitter.com/example', 'https://www.twitter.com/example'),
        ('', ''),
        (None, ''),
    ),
)
def test_twitter_url_clean(value, expected):
    field = forms.TwitterURLField()
    assert field.to_python(value) == expected


@pytest.mark.parametrize(
    'value,expected',
    (
        ('Foo bar on linked in', ''),
        ('www.linkedin.com/example', 'https://www.linkedin.com/company/example'),
        ('foo', 'https://www.linkedin.com/company/foo'),
        ('@foo', 'https://www.linkedin.com/company/foo'),
        ('https://www.linkedin.com/foo', 'https://www.linkedin.com/company/foo'),
        ('', ''),
        (None, ''),
    ),
)
def test_linkedin_url_clean(value, expected):
    field = forms.LinkedInURLField()
    assert field.to_python(value) == expected


@pytest.mark.parametrize(
    'value,expected',
    (
        ('', company_types.SOLE_TRADER),
        (None, company_types.SOLE_TRADER),
        ('1234567', company_types.COMPANIES_HOUSE),
        ('THERE IS NO IN ENGLAND ', company_types.SOLE_TRADER),
        ('N/A', company_types.SOLE_TRADER),
        ('N/a', company_types.SOLE_TRADER),
        ('n/a', company_types.SOLE_TRADER),
    ),
)
def test_company_type_parser(value, expected):
    assert forms.company_type_parser(value) == expected
