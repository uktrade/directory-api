from django.template.loader import render_to_string


def test_confirmation_email():
    context = {
        'url': 'http://confirm.com'
    }
    html = render_to_string('confirmation_email.html', context)
    assert 'http://confirm.com' in html
