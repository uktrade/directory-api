from django.core.cache import cache
from django.core.mail import EmailMultiAlternatives

from api.celery import app
from notifications import notifications, models
from user.models import User as Supplier


def lock_acquired(lock_name):
    """ Returns False if the lock was already set in the last 20 hours

    Multiple celery beat schedulers are running at the same time, which
    results in duplicated scheduled tasks. Cache-lock mechanism is used to
    assure that only one task gets executed. Lock expires after 20 hours

    """
    return cache.add(lock_name, 'acquired', 72000)


@app.task
def no_case_studies():
    if lock_acquired('no_case_studies'):
        notifications.no_case_studies()


@app.task
def hasnt_logged_in():
    if lock_acquired('hasnt_logged_in'):
        notifications.hasnt_logged_in()


@app.task
def verification_code_not_given():
    if lock_acquired('verification_code_not_given'):
        notifications.verification_code_not_given()


@app.task
def new_companies_in_sector():
    if lock_acquired('new_companies_in_sector'):
        notifications.new_companies_in_sector()


def send_email(subject,
               text_body,
               html_body,
               recipient_email,
               from_email):
    message = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        to=[recipient_email],
        from_email=from_email,
    )
    message.attach_alternative(html_body, "text/html")
    message.send()


@app.task(autoretry_for=(TimeoutError, ))
def send_supplier_email(subject,
                        text_body,
                        html_body,
                        recipient_email,
                        from_email,
                        category,
                        supplier_id):
    send_email(subject, text_body, html_body, recipient_email, from_email)
    supplier = Supplier.objects.get(pk=supplier_id)
    return models.SupplierEmailNotification.objects.create(
        supplier=supplier, category=category)


@app.task(autoretry_for=(TimeoutError, ))
def send_anon_email(subject,
                    text_body,
                    html_body,
                    recipient_email,
                    from_email,
                    category):
    send_email(subject, text_body, html_body, recipient_email, from_email)
    return models.AnonymousEmailNotification.objects.create(
        email=recipient_email, category=category)
