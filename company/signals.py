from django.conf import settings

from company.stannp import stannp_client


def send_verification_letter(sender, instance, *args, **kwargs):
    enabled = settings.FEATURE_VERIFICATION_LETTERS_ENABLED
    if not enabled or instance.is_verification_letter_sent:
        return

    stannp_client.send_letter(
        template=settings.STANNP_VERIFICATION_LETTER_TEMPLATE_ID,
        recipient=instance.contact_details,
        pages="Verification code: {}".format(instance.verification_code)
    )

    instance.is_verification_letter_sent = True
    instance.save()
