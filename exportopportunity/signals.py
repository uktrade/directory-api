from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_opportunity_to_post(sender, instance, *args, **kwargs):
    message = render_to_string(
        'email/opportunity-submitted.txt', {'opportunity': instance}
    )
    send_mail(
        subject=settings.SUBJECT_EXPORT_OPPORTUNITY_CREATED,
        message=message,
        from_email=settings.FAS_FROM_EMAIL,
        recipient_list=(settings.RECIPIENT_EMAIL_EXPORT_OPPORTUNITY_CREATED,),
    )
