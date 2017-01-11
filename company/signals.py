import datetime

from django.conf import settings

from company.stannp import stannp_client
from company import helpers


def send_verification_letter(sender, instance, *args, **kwargs):
    is_disabled = not settings.FEATURE_VERIFICATION_LETTERS_ENABLED
    is_address_unknown = not helpers.is_address_known(instance)
    is_already_sent = instance.is_verification_letter_sent
    if is_disabled or is_already_sent or is_address_unknown:
        return

    recipient = {
        'postal_full_name': instance.postal_full_name,
        'address_line_1': instance.address_line_1,
        'address_line_2': instance.address_line_2,
        'locality': instance.locality,
        'country': instance.country,
        'postal_code': instance.postal_code,
        'po_box': instance.po_box,
        'custom_fields': [
            ('full_name', instance.postal_full_name),
            ('company_name', instance.name),
            ('verification_code', instance.verification_code),
            ('date', datetime.date.today().strftime('%d/%m/%Y')),
            ('company', instance.name),
        ]
    }

    stannp_client.send_letter(
        template=settings.STANNP_VERIFICATION_LETTER_TEMPLATE_ID,
        recipient=recipient
    )

    instance.is_verification_letter_sent = True
    instance.save()
