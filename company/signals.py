import datetime

from django.conf import settings

from company.stannp import stannp_client


def send_verification_letter(sender, instance, *args, **kwargs):
    enabled = settings.FEATURE_VERIFICATION_LETTERS_ENABLED
    if not enabled or instance.is_verification_letter_sent:
        return

    recipient = instance.contact_details.copy()
    recipient['custom_fields'] = [
        ('full_name', recipient['postal_full_name']),
        ('company_name', instance.name),
        ('verification_code', instance.verification_code),
        ('date', datetime.date.today().strftime('%d/%m/%Y'))
    ]

    stannp_client.send_letter(
        template=settings.STANNP_VERIFICATION_LETTER_TEMPLATE_ID,
        recipient=recipient
    )

    instance.is_verification_letter_sent = True
    instance.save()
