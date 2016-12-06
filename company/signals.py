from django.conf import settings
from django.utils.crypto import get_random_string

from company.stannp import stannp_client


class NoCompanyAddressException(Exception):
    pass


def send_verification_letter(sender, instance, created, *args, **kwargs):
    enabled = settings.FEATURE_VERIFICATION_LETTERS_ENABLED
    if not enabled or not created or instance.verified_with_code:
        return

    if not instance.contact_details:
        raise NoCompanyAddressException(
            "Company registered address is required "
            "to send a verification letter"
        )

    if not instance.verification_code:
        instance.verification_code = get_random_string(
            length=12, allowed_chars='0123456789'
        )
        instance.save()

    stannp_client.send_letter(
        template=settings.STANNP_VERIFICATION_LETTER_TEMPLATE_ID,
        recipient=instance.contact_details,
        pages="Verification code: {}".format(instance.verification_code)
    )
