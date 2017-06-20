from django.conf import settings
from django.utils import timezone

from company.utils import send_verification_letter


def send_first_verification_letter(sender, instance, *args, **kwargs):
    is_disabled = not settings.FEATURE_VERIFICATION_LETTERS_ENABLED
    has_invalid_address = not instance.has_valid_address()
    is_already_sent = instance.is_verification_letter_sent
    if is_disabled or is_already_sent or has_invalid_address:
        return

    send_verification_letter(company=instance)


def publish_companies_that_meet_criteria(sender, instance, *args, **kwargs):
    if not instance.is_published:
        instance.is_published = bool(
            (instance.description or instance.summary) and
            instance.email_address and
            instance.verified_with_code
        )


def store_date_published(sender, instance, *args, **kwargs):
    if instance.is_published and not instance.date_published:
        instance.date_published = timezone.now()


def save_to_elasticsearch(sender, instance, *args, **kwargs):
    if instance.is_published:
        instance.to_doc_type().save()


def deactivate_trusted_source_signup_code(sender, instance, *args, **kwargs):
    # django throws "AppRegistreyNotReady" if model imported at module level
    from enrolment.models import TrustedSourceSignupCode
    if not instance.pk:
        queryset = TrustedSourceSignupCode.objects.filter(
            company_number=instance.number
        )
        queryset.update(is_active=False)
