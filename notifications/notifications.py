from datetime import timedelta, datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

from directory_sso_api_client.client import DirectorySSOAPIClient

from user.models import User as Supplier
from notifications import models, constants


sso_api_client = DirectorySSOAPIClient(
    base_url=settings.SSO_API_CLIENT_BASE_URL,
    api_key=settings.SSO_API_CLIENT_KEY,
)


def send_email_notifications(
    suppliers, text_template, html_template, subject,
    notification_category, extra_context
):
    """Helper for sending notification emails"""
    for supplier in suppliers:
        context = {
            'full_name': supplier.name,
            'zendesk_url': settings.ZENDESK_URL,
        }
        context.update(extra_context)
        text_body = render_to_string(text_template, context)
        html_body = render_to_string(html_template, context)
        message = EmailMultiAlternatives(
            subject=subject,
            body=text_body,
            to=[supplier.company_email],
        )
        message.attach_alternative(html_body, "text/html")
        message.send()
        models.SupplierEmailNotification.objects.create(
            supplier=supplier, category=notification_category)


def no_case_studies():
    days_ago = datetime.utcnow() - timedelta(
        days=settings.NO_CASE_STUDIES_DAYS)
    suppliers = Supplier.objects.filter(
        company__supplier_case_studies__isnull=True,
        date_joined__year=days_ago.year,
        date_joined__month=days_ago.month,
        date_joined__day=days_ago.day,
        unsubscribed=False,
    ).exclude(
        supplieremailnotification__category=constants.NO_CASE_STUDIES,
    )
    send_email_notifications(
        suppliers,
        'no_case_studies_email.txt',
        'no_case_studies_email.html',
        settings.NO_CASE_STUDIES_SUBJECT,
        constants.NO_CASE_STUDIES,
        {'case_study_url': settings.CASE_STUDY_URL}
    )


def hasnt_logged_in():
    days_ago = datetime.utcnow() - timedelta(
        days=settings.HASNT_LOGGED_IN_DAYS)
    start_datetime = days_ago.replace(
        hour=0, minute=0, second=0, microsecond=0)
    end_datetime = days_ago.replace(
        hour=23, minute=59, second=59, microsecond=999999)
    login_data = sso_api_client.user.get_last_login(
        start=start_datetime, end=end_datetime).json()
    supplier_ids = [supplier['id'] for supplier in login_data]
    suppliers = Supplier.objects.filter(
        sso_id__in=supplier_ids
    ).exclude(
        supplieremailnotification__category=constants.HASNT_LOGGED_IN,
    )
    send_email_notifications(
        suppliers,
        'hasnt_logged_in_email.txt',
        'hasnt_logged_in_email.html',
        settings.HASNT_LOGGED_IN_SUBJECT,
        constants.HASNT_LOGGED_IN,
        {'login_url': settings.LOGIN_URL}
    )


def verification_code_not_given():
    extra_context = {
        'verification_url': settings.VERIFICATION_CODE_URL,
    }

    # 1st email (after 8 days)
    days_ago = datetime.utcnow() - timedelta(
        days=settings.VERIFICATION_CODE_NOT_GIVEN_DAYS)
    suppliers = Supplier.objects.filter(
        company__verified_with_code=False,
        date_joined__year=days_ago.year,
        date_joined__month=days_ago.month,
        date_joined__day=days_ago.day,
        unsubscribed=False,
    ).exclude(
        supplieremailnotification__category=constants.
        VERIFICATION_CODE_NOT_GIVEN,
    )
    send_email_notifications(
        suppliers,
        'verification_code_not_given_email.txt',
        'verification_code_not_given_email.html',
        settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT,
        constants.VERIFICATION_CODE_NOT_GIVEN,
        extra_context
    )

    # 2nd email (after 16 days)
    days_ago = datetime.utcnow() - timedelta(
        days=settings.VERIFICATION_CODE_NOT_GIVEN_DAYS_2ND_EMAIL)
    suppliers = Supplier.objects.filter(
        company__verified_with_code=False,
        date_joined__year=days_ago.year,
        date_joined__month=days_ago.month,
        date_joined__day=days_ago.day,
        unsubscribed=False,
    ).exclude(
        supplieremailnotification__category=constants.
        VERIFICATION_CODE_2ND_EMAIL,
    )
    send_email_notifications(
        suppliers,
        'verification_code_not_given_2nd_email.txt',
        'verification_code_not_given_2nd_email.html',
        settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT_2ND_EMAIL,
        constants.VERIFICATION_CODE_2ND_EMAIL,
        extra_context
    )


def new_companies_in_sector():
    # TODO: ED-919
    pass
