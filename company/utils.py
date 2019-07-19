import datetime

from django.conf import settings
from django.utils import timezone

from company.stannp import stannp_client

from directory_forms_api_client import actions


def send_verification_letter(company, form_url=None):
    if settings.FEATURE_VERIFICATION_LETTERS_VIA_GOVNOTIFY_ENABLED:
        recipient = {
            'address_line_1': company.postal_full_name,
            'address_line_2': company.address_line_1,
            'address_line_3': company.address_line_2,
            'address_line_4': company.locality,
            'address_line_5': company.country,
            'address_line_6': company.po_box,
            'postcode': company.postal_code,
            'full_name': company.postal_full_name,
            'company_name': company.name,
            'verification_code': company.verification_code,
        }

        action = actions.GovNotifyLetterAction(
            template_id=settings.GOVNOTIFY_VERIFICATION_LETTER_TEMPLATE_ID,
            form_url=form_url,

        )
        action.save(recipient)

    else:
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
