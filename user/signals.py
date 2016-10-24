import uuid

from notifications_python_client.notifications import NotificationsAPIClient

from django.conf import settings


def send_confirmation_email(sender, instance, created, *args, **kwargs):
    if not created or not instance.company_email:
        return

    service_id = settings.GOV_NOTIFY_SERVICE_ID
    api_key = settings.GOV_NOTIFY_API_KEY
    template_id = settings.CONFIRMATION_EMAIL_TEMPLATE_ID

    instance.confirmation_code = str(uuid.uuid4())
    instance.save()

    notifications_client = NotificationsAPIClient(
        service_id=service_id, api_key=api_key)
    url = settings.CONFIRMATION_URL_TEMPLATE % instance.confirmation_code
    notifications_client.send_email_notification(
        instance.company_email, template_id,
        personalisation={'confirmation url': url})
