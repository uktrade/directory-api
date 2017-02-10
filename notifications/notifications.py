from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import timezone

from user.models import User as Supplier
from notifications.models import SupplierEmailNotification


def no_case_studies():
    # TODO: ED-918
    pass


def hasnt_logged_in():
    # TODO: ED-921
    pass


def verification_code_not_given():
    eight_days_ago = timezone.now() - timedelta(days=8)
    suppliers = Supplier.objects.filter(
        company__verified_with_code=False,
        supplieremailnotification__isnull=True,
        date_joined__year=eight_days_ago.year,
        date_joined__month=eight_days_ago.month,
        date_joined__day=eight_days_ago.day,
    )
    supplier_emails = suppliers.values_list('company_email', flat=True)
    text_body = render_to_string('verification_code_not_given_email.txt', {})
    html_body = render_to_string('verification_code_not_given_email.html', {})

    message = EmailMultiAlternatives(
        subject=settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT,
        body=text_body,
        to=supplier_emails,
    )
    message.attach_alternative(html_body, "text/html")
    message.send()

    notification_objs = [
        SupplierEmailNotification(supplier=supplier,
                                  category='verification_code_not_given')
        for supplier in suppliers
    ]
    SupplierEmailNotification.objects.bulk_create(notification_objs)


def new_companies_in_sector():
    # TODO: ED-919
    pass
