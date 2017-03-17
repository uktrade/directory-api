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
