import pytest
from django.core import mail

from core.tasks import send_email


@pytest.mark.django_db
def test_send_email():
    mail.outbox = []
    subject = 'Foo'
    text_body = 'bar'
    html_body = '<a>bar</a>'
    recipient_email = 'testo@useri.com'
    from_email = 'test@foo.bar'

    send_email(
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        recipient_email=recipient_email,
        from_email=from_email,
    )

    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.body == text_body
    assert email.to[0] == recipient_email
    assert email.from_email == from_email
    assert email.subject == subject
    assert email.alternatives[0] == (html_body, 'text/html')
