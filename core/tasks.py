from django.core.mail import EmailMultiAlternatives
from django.core.management import call_command

from conf.celery import app


@app.task(autoretry_for=(TimeoutError,))
def send_email(subject, text_body, html_body, recipient_email, from_email):
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        to=[recipient_email],
        from_email=from_email,
    )
    message.attach_alternative(html_body, "text/html")
    message.send()


@app.task()
def elsaticsearch_migrate():
    call_command('elasticsearch_migrate')
