from django.core.mail import EmailMultiAlternatives

from api.celery import app


@app.task(autoretry_for=(TimeoutError, ))
def send_email(
    subject, text_body, html_body, recipient_email, from_email
):
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        to=[recipient_email],
        from_email=from_email,
    )
    message.attach_alternative(html_body, "text/html")
    message.send()
