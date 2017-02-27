import datetime

from django.conf import settings
from django.utils import timezone

from company.stannp import stannp_client


def send_verification_letter(sender, instance, *args, **kwargs):
    is_disabled = not settings.FEATURE_VERIFICATION_LETTERS_ENABLED
    has_invalid_address = not instance.has_valid_address()
    is_already_sent = instance.is_verification_letter_sent
    if is_disabled or is_already_sent or has_invalid_address:
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


def publish_companies_that_meet_criteria(sender, instance, *args, **kwargs):
    if not instance.is_published:
        instance.is_published = bool(
            (instance.description or instance.summary) and
            instance.email_address and
            instance.verified_with_code
        )


def fill_in_verification_date(sender, instance, *args, **kwargs):
    was_verified = sender.objects.filter(
        pk=instance.pk, verified_with_code=True).exists()
    if instance.verified_with_code and not was_verified:
        instance.verification_date = timezone.now()
