import pytest
from django.core import mail

from notifications.models import AnonymousEmailNotification, \
    SupplierEmailNotification
from notifications.tasks import send_anon_email, send_supplier_email
from supplier.tests.factories import SupplierFactory


@pytest.mark.django_db
def test_send_supplier_email():
    supplier = SupplierFactory()
    mail.outbox = []
    subject = 'Foo'
    text_body = 'bar'
    html_body = '<a>bar</a>'
    recipient_email = 'testo@useri.com'
    from_email = 'test@foo.bar'
    category = 'test'

    result = send_supplier_email(
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        recipient_email=recipient_email,
        from_email=from_email,
        supplier_id=supplier.pk,
        category=category
    )

    assert isinstance(result, SupplierEmailNotification)
    assert result.supplier == supplier
    assert result.category == category
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.body == text_body
    assert email.to[0] == recipient_email
    assert email.from_email == from_email
    assert email.subject == subject
    assert email.alternatives[0] == (html_body, 'text/html')


@pytest.mark.django_db
def test_send_anon_email():
    mail.outbox = []
    subject = 'Foo'
    text_body = 'bar'
    html_body = '<a>bar</a>'
    recipient_email = 'testo@useri.com'
    from_email = 'test@foo.bar'
    category = 'test'

    result = send_anon_email(
        subject=subject,
        text_body=text_body,
        html_body=html_body,
        recipient_email=recipient_email,
        from_email=from_email,
        category=category
    )

    assert isinstance(result, AnonymousEmailNotification)
    assert result.category == category
    assert result.email == recipient_email
    assert len(mail.outbox) == 1
    email = mail.outbox[0]
    assert email.body == text_body
    assert email.to[0] == recipient_email
    assert email.from_email == from_email
    assert email.subject == subject
    assert email.alternatives[0] == (html_body, 'text/html')
