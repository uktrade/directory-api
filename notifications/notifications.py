from datetime import timedelta, datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from user.models import User as Supplier
from notifications.models import SupplierEmailNotification


def no_case_studies():
    days_ago = datetime.utcnow() - timedelta(
        days=settings.NO_CASE_STUDIES_DAYS)
    suppliers = Supplier.objects.filter(
        company__supplier_case_studies__isnull=True,
        date_joined__year=days_ago.year,
        date_joined__month=days_ago.month,
        date_joined__day=days_ago.day,
    ).exclude(
        supplieremailnotification__category='no_case_studies',
    )

    for supplier in suppliers:
        context = {'full_name': supplier.name}
        text_body = render_to_string('no_case_studies_email.txt', context)
        html_body = render_to_string('no_case_studies_email.html', context)
        message = EmailMultiAlternatives(
            subject=settings.NO_CASE_STUDIES_SUBJECT,
            body=text_body,
            to=[supplier.company_email],
        )
        message.attach_alternative(html_body, "text/html")
        message.send()

    notification_objs = [
        SupplierEmailNotification(supplier=supplier,
                                  category='no_case_studies')
        for supplier in suppliers
    ]
    SupplierEmailNotification.objects.bulk_create(notification_objs)


def hasnt_logged_in():
    # TODO: ED-921
    pass


def verification_code_not_given():
    # TODO: ED-917
    pass


def new_companies_in_sector():
    # TODO: ED-919
    pass
