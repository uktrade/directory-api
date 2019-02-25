import pytest

from company import forms, models


@pytest.mark.parametrize('value,expected', (
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
))
def test_company_number_clean(value, expected):
    field = forms.CompanyNumberField(max_length=8)
    assert field.to_python(value) == expected


@pytest.mark.parametrize('value,expected', (
    ('www.example.com', 'http://www.example.com'),
    ('https://www.example.co.uk', 'https://www.example.co.uk'),
    (None, None),
    ('', None),
))
def test_company_url_clean(value, expected):
    field = forms.CompanyUrlField()
    assert field.to_python(value) == expected


@pytest.mark.parametrize('value,expected', (
    ('Foo bar on facebook', None),
    ('www.facebook.com/example', 'https://www.facebook.com/example'),
    ('example', 'https://www.facebook.com/example'),
    ('@example', 'https://www.facebook.com/example'),
    ('https://www.facebook.com/example', 'https://www.facebook.com/example'),
    ('', None),
    (None, None),
))
def test_facebook_url_clean(value, expected):
    field = forms.FacebookURLField()
    assert field.to_python(value) == expected


@pytest.mark.parametrize('value,expected', (
    ('Foo bar on twitter', None),
    ('www.twitter.com/example', 'https://www.twitter.com/example'),
    ('example', 'https://www.twitter.com/example'),
    ('@example', 'https://www.twitter.com/example'),
    ('https://www.twitter.com/example', 'https://www.twitter.com/example'),
    ('', None),
    (None, None),
))
def test_twitter_url_clean(value, expected):
    field = forms.TwitterURLField()
    assert field.to_python(value) == expected


@pytest.mark.parametrize('value,expected', (
    ('Foo bar on linked in', None),
    ('www.linkedin.com/example', 'https://www.linkedin.com/company/example'),
    ('foo', 'https://www.linkedin.com/company/foo'),
    ('@foo', 'https://www.linkedin.com/company/foo'),
    ('https://www.linkedin.com/foo', 'https://www.linkedin.com/company/foo'),
    ('', None),
    (None, None),
))
def test_linkedin_url_clean(value, expected):
    field = forms.LinkedInURLField()
    assert field.to_python(value) == expected


@pytest.mark.parametrize('value,expected', (
    ('', models.Company.SOLE_TRADER),
    (None, models.Company.SOLE_TRADER),
    ('1234567', models.Company.COMPANIES_HOUSE)
))
def test_company_type_parser(value, expected):
    assert forms.company_type_parser(value) == expected
