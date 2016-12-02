import uuid

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_confirmation_email(sender, instance, created, *args, **kwargs):
    already_confirmed = instance.company_email_confirmed
    if not created or not instance.company_email or already_confirmed:
        return

    if not instance.company_email_confirmation_code:
        instance.company_email_confirmation_code = str(uuid.uuid4())
        instance.save()

    subject = settings.COMPANY_EMAIL_CONFIRMATION_SUBJECT
    from_email = settings.COMPANY_EMAIL_CONFIRMATION_FROM
    confirmation_url = "{confirmation_url}?code={confirmation_code}".format(
        confirmation_url=settings.COMPANY_EMAIL_CONFIRMATION_URL,
        confirmation_code=instance.company_email_confirmation_code
    )

    context = {'confirmation_url': confirmation_url}
    text_body = render_to_string('confirmation_email.txt', context)
    html_body = render_to_string('confirmation_email.html', context)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=from_email,
        to=[instance.company_email]
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send()
