from notifications_python_client.notifications import NotificationsAPIClient

from django.conf import settings
from django.utils.crypto import get_random_string


notifications_client = NotificationsAPIClient(
    service_id=settings.GOV_NOTIFY_SERVICE_ID,
    api_key=settings.GOV_NOTIFY_API_KEY,
)


def generate_sms_verification_code():
    return get_random_string(6).lower()


def send_verification_code_via_sms(phone_number):
    verification_code = generate_sms_verification_code()
    notifications_client.send_sms_notification(
        user.company_email, template_id,
        personalisation={
            'service_name': settings.GOV_NOTIFY_SERVICE_NAME,
            'verification_code': verification_code,
        }
    )
    return verification_code
