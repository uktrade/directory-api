from datetime import timedelta, datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from user.models import User as Supplier
from notifications import models, constants


def no_case_studies():
    days_ago = datetime.utcnow() - timedelta(
        days=settings.NO_CASE_STUDIES_DAYS)
    suppliers = Supplier.objects.filter(
        company__supplier_case_studies__isnull=True,
        date_joined__year=days_ago.year,
        date_joined__month=days_ago.month,
        date_joined__day=days_ago.day,
    ).exclude(
        supplieremailnotification__category=constants.NO_CASE_STUDIES,
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
        models.SupplierEmailNotification.objects.create(
            supplier=supplier, category=constants.NO_CASE_STUDIES)


def hasnt_logged_in():
    # TODO: ED-921
    pass


def verification_code_not_given():
    days_ago = datetime.utcnow() - timedelta(
        days=settings.VERIFICATION_CODE_NOT_GIVEN_DAYS)
    suppliers = Supplier.objects.filter(
        company__verified_with_code=False,
        date_joined__year=days_ago.year,
        date_joined__month=days_ago.month,
        date_joined__day=days_ago.day,
    ).exclude(
        supplieremailnotification__category=constants.
        VERIFICATION_CODE_NOT_GIVEN,
    )

    for supplier in suppliers:
        context = {'full_name': supplier.name}
        text_body = render_to_string(
            'verification_code_not_given_email.txt', context)
        html_body = render_to_string(
            'verification_code_not_given_email.html', context)
        message = EmailMultiAlternatives(
            subject=settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT,
            body=text_body,
            to=[supplier.company_email],
        )
        message.attach_alternative(html_body, "text/html")
        message.send()
        models.SupplierEmailNotification.objects.create(
            supplier=supplier, category=constants.VERIFICATION_CODE_NOT_GIVEN)

    days_ago = datetime.utcnow() - timedelta(
        days=settings.VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL)
    suppliers = Supplier.objects.filter(
        company__verified_with_code=False,
        date_joined__year=days_ago.year,
        date_joined__month=days_ago.month,
        date_joined__day=days_ago.day,
    ).exclude(
        supplieremailnotification__category=constants.
        VERIFICATION_CODE_NOT_GIVEN,
    )

    for supplier in suppliers:
        context = {'full_name': supplier.name}
        text_body = render_to_string(
            'verification_code_not_given_2nd_email.txt', context)
        html_body = render_to_string(
            'verification_code_not_given_2nd_email.html', context)
        message = EmailMultiAlternatives(
            subject=settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT,
            body=text_body,
            to=[supplier.company_email],
        )
        message.attach_alternative(html_body, "text/html")
        message.send()
        models.SupplierEmailNotification.objects.create(
            supplier=supplier, category=constants.VERIFICATION_CODE_NOT_GIVEN)


def new_companies_in_sector():
    # TODO: ED-919
    pass
