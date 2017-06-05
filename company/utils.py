import datetime

from django.conf import settings
from django.utils import timezone

from company.stannp import stannp_client


def send_verification_letter(company):
    recipient = {
        'postal_full_name': company.postal_full_name,
        'address_line_1': company.address_line_1,
        'address_line_2': company.address_line_2,
        'locality': company.locality,
        'country': company.country,
        'postal_code': company.postal_code,
        'po_box': company.po_box,
        'custom_fields': [
            ('full_name', company.postal_full_name),
            ('company_name', company.name),
            ('verification_code', company.verification_code),
            ('date', datetime.date.today().strftime('%d/%m/%Y')),
            ('company', company.name),
        ]
    }

    stannp_client.send_letter(
        template=settings.STANNP_VERIFICATION_LETTER_TEMPLATE_ID,
        recipient=recipient
    )

    company.is_verification_letter_sent = True
    company.date_verification_letter_sent = timezone.now()
    company.save()
