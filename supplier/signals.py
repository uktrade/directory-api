from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_confirmation_email(sender, instance, created, *args, **kwargs):
    sync_creation = settings.FEATURE_SYNCHRONOUS_PROFILE_CREATION
    if not created or not instance.company_email or sync_creation:
        return

    context = {'url': settings.COMPANY_EMAIL_CONFIRMATION_URL}
    text_body = render_to_string('confirmation_email.txt', context)
    html_body = render_to_string('confirmation_email.html', context)

    message = EmailMultiAlternatives(
        subject=settings.COMPANY_EMAIL_CONFIRMATION_SUBJECT,
        body=text_body,
        from_email=settings.COMPANY_EMAIL_CONFIRMATION_FROM,
        to=[instance.company_email]
    )
    message.attach_alternative(html_body, "text/html")
    message.send()
