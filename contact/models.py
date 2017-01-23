from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import models

from directory_validators.constants import choices

from api.model_utils import TimeStampedModel
from company.models import Company


class MessageToSupplier(TimeStampedModel):
    sender_email = models.EmailField(unique=True)
    sender_name = models.CharField(max_length=255)
    sender_company_name = models.CharField(max_length=255)
    sender_country = models.CharField(max_length=255)
    sector = models.CharField(
        choices=choices.COMPANY_CLASSIFICATIONS,
        max_length=255,
    )
    recipient = models.ForeignKey(
        Company, related_name='messages', null=True
    )
    is_sent = models.BooleanField(default=False)

    def __str__(self):
        return 'Message from {} to {}'.format(
            self.sender_email, self.recipient
        )

    def send(self, sender_body, sender_subject):
        if self.is_sent:
            return

        context = {
            'sender_email': self.sender_email,
            'sender_name': self.sender_name,
            'sender_company_name': self.sender_company_name,
            'sender_country': self.sender_country,
            'sector': self.sector,
            'sender_subject': sender_subject,
            'sender_body': sender_body,
            'recipient_name': self.recipient.email_full_name,
        }
        text_body = render_to_string('email_to_supplier.txt', context)
        html_body = render_to_string('email_to_supplier.html', context)

        message = EmailMultiAlternatives(
            subject=settings.CONTACT_SUPPLIER_SUBJECT,
            body=text_body,
            from_email=settings.CONTACT_SUPPLIER_FROM_EMAIL,
            reply_to=(self.sender_email, ),
            to=(self.recipient.email_address, ),
        )
        message.attach_alternative(html_body, "text/html")
        message.send()

        self.is_sent = True
        self.save()
