from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string

from exportopportunity import helpers


def send_opportunity_to_post(sender, instance, *args, **kwargs):
    message = render_to_string(
        instance.email_template_name,
        {'instance': instance}
    )
    recipient_list = helpers.get_ita_email(
        campaign=instance.campaign, country=instance.country,
    )
    if recipient_list:
        send_mail(
            subject=settings.SUBJECT_EXPORT_OPPORTUNITY_CREATED,
            message=message,
            from_email=settings.FAS_FROM_EMAIL,
            recipient_list=recipient_list,
        )
