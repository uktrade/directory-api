from django.template.loader import render_to_string


UNSUBSCRIBE_LABEL = 'Unsubscribe'


def test_confirmation_email():
    context = {
        'url': 'http://confirm.com'
    }
    html = render_to_string('confirmation_email.html', context)
    assert 'http://confirm.com' in html


def test_email_unsubscribe():
    context = {
        'unsubscribe_url': 'http://unsubscribe.com'
    }
    html = render_to_string('email.html', context)
    assert context['unsubscribe_url'] in html
    assert UNSUBSCRIBE_LABEL in html


def test_email_unsubscribe_missing():
    html = render_to_string('email.html', {})

    assert UNSUBSCRIBE_LABEL not in html


def test_new_companies_in_sector_email_utm(settings):
    template_names = [
        'new_companies_in_sector_email.html',
        'new_companies_in_sector_email.txt',
    ]
    settings.FAS_COMPANY_PROFILE_URL = 'http://profile/{number}'
    context = {
        'companies': [
            {
                'number': 1234
            }
        ],
        'utm_params': 'thing=abc'
    }

    for template_name in template_names:
        html = render_to_string(template_name, context)
        assert 'http://profile/1234?thing=abc' in html
