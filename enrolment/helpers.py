from notifications_python_client.notifications import NotificationsAPIClient

from django.conf import settings
from django.utils.crypto import get_random_string


def generate_sms_verification_code():
    return get_random_string(length=6, allowed_chars='0123456789')


def send_verification_code_via_sms(phone_number):
    notifications_client = NotificationsAPIClient(
        service_id=settings.GOV_NOTIFY_SERVICE_ID,
        api_key=settings.GOV_NOTIFY_API_KEY,
    )
    verification_code = generate_sms_verification_code()
    notifications_client.send_sms_notification(
        phone_number,
        settings.GOV_NOTIFY_SERVICE_VERIFICATION_TEMPLATE_NAME,
        personalisation={
            'verification_code': verification_code,
        }
    )
    return verification_code
