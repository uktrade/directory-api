import django.utils.html

from conf.celery import app
from company.models import Company
from contact.models import MessageToSupplier


def strip_tags_and_escape(string):
    stripped = django.utils.html.strip_tags(string)
    return django.utils.html.escape(stripped)


@app.task
def message_to_supplier(data):
    recipient = Company.objects.get(
        number=data['recipient_company_number']
    )
    message_to_supplier = MessageToSupplier.objects.create(
        sender_email=data['sender_email'],
        sender_name=data['sender_name'],
        sender_company_name=data['sender_company_name'],
        sender_country=data['sender_country'],
        sector=data['sector'],
        recipient=recipient
    )

    message_to_supplier.send(
        sender_subject=strip_tags_and_escape(
            data['subject']
        ),
        sender_body=strip_tags_and_escape(
            data['body']
        ),
    )
