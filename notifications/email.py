import abc
import csv
import os
from collections import namedtuple

from django.conf import settings
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from notifications_python_client import prepare_upload

from core.helpers import notifications_client
from notifications import constants, helpers, models, tokens

Recipient = namedtuple('Recipient', ['email', 'name'])


class NotificationBase(abc.ABC):
    category = abc.abstractproperty()
    from_email = abc.abstractproperty()
    html_template = abc.abstractproperty()
    recipient = abc.abstractproperty()
    subject = abc.abstractproperty()
    text_template = abc.abstractproperty()
    unsubscribe_url = abc.abstractproperty()
    zendesk_url = settings.ZENDESK_URL

    def get_context_data(self, **kwargs):
        return {
            'full_name': self.recipient.name,
            'zendesk_url': self.zendesk_url,
            'unsubscribe_url': self.unsubscribe_url,
            **kwargs,
        }

    def get_bodies(self):
        context = self.get_context_data()
        text_body = render_to_string(self.text_template, context)
        html_body = render_to_string(self.html_template, context)
        return text_body, html_body

    def send(self):
        raise NotImplementedError


class SupplierNotificationBase(NotificationBase):
    from_email = settings.FAB_FROM_EMAIL

    def __init__(self, company_user):
        self.company_user = company_user

    @property
    def recipient(self):
        return Recipient(name=self.company_user.name, email=self.company_user.company_email)

    # TODO: deprecated - to be removed
    # def send(self):
    #     text_body, html_body = self.get_bodies()
    #     models.SupplierEmailNotification.objects.create(company_user=self.company_user, category=self.category)
    #     core.tasks.send_email.delay(
    #         subject=self.subject,
    #         text_body=text_body,
    #         html_body=html_body,
    #         recipient_email=self.recipient.email,
    #         from_email=self.from_email,
    #     )


class AnonymousSubscriberNotificationBase(NotificationBase):
    from_email = settings.FAS_FROM_EMAIL

    def __init__(self, subscriber):
        self.subscriber = subscriber
        self.notification = models.AnonymousEmailNotification.objects.create(
            email=self.recipient.email, category=self.category
        )

    @property
    def recipient(self):
        return Recipient(name=self.subscriber['name'], email=self.subscriber['email'])

    # TODO: deprecated - to be removed
    # def send(self):
    #     text_body, html_body = self.get_bodies()
    #     core.tasks.send_email.delay(
    #         subject=self.subject,
    #         text_body=text_body,
    #         html_body=html_body,
    #         recipient_email=self.recipient.email,
    #         from_email=self.from_email,
    #     )


class VerificationWaitingNotification(SupplierNotificationBase):
    html_template = 'verification_code_not_given_email.html'
    category = constants.VERIFICATION_CODE_NOT_GIVEN
    subject = settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT
    text_template = 'verification_code_not_given_email.txt'
    unsubscribe_url = settings.FAB_NOTIFICATIONS_UNSUBSCRIBE_URL
    template_id = settings.GOVNOTIFY_VERIFICATION_CODE_NOT_GIVEN_TEMPLATE_ID

    def get_context_data(self):
        return super().get_context_data(verification_url=settings.VERIFICATION_CODE_URL)

    def send(self):
        notifications_client.send_email_notification(
            email_address=self.recipient.email,
            template_id=self.template_id,
            personalisation={
                'verification_url': settings.VERIFICATION_CODE_URL,
                'zendesk_url': settings.ZENDESK_URL,
            },
        )


class VerificationStillWaitingNotification(SupplierNotificationBase):
    html_template = 'verification_code_not_given_2nd_email.html'
    category = constants.VERIFICATION_CODE_2ND_EMAIL
    subject = settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT_2ND_EMAIL
    text_template = 'verification_code_not_given_2nd_email.txt'
    unsubscribe_url = settings.FAB_NOTIFICATIONS_UNSUBSCRIBE_URL
    template_id = settings.GOVNOTIFY_VERIFICATION_CODE_NOT_GIVEN_2ND_EMAIL_TEMPLATE_ID

    def get_context_data(self):
        return super().get_context_data(
            verification_url=settings.VERIFICATION_CODE_URL,
        )

    def send(self):
        notifications_client.send_email_notification(
            email_address=self.recipient.email,
            template_id=self.template_id,
            personalisation={
                'verification_url': settings.VERIFICATION_CODE_URL,
                'zendesk_url': settings.ZENDESK_URL,
            },
        )


class NewCompaniesInSectorNotification(AnonymousSubscriberNotificationBase):
    html_template = 'new_companies_in_sector_email.html'
    category = constants.NEW_COMPANIES_IN_SECTOR
    subject = settings.NEW_COMPANIES_IN_SECTOR_SUBJECT
    text_template = 'new_companies_in_sector_email.txt'
    template_id = settings.GOVNOTIFY_NEW_COMPANIES_IN_SECTOR_TEMPLATE_ID

    def __init__(self, subscriber, companies):
        self.companies = companies
        super().__init__(subscriber=subscriber)

    @property
    def unsubscribe_url(self):
        uidb64 = urlsafe_base64_encode(force_bytes(self.notification.pk))
        token = tokens.anonymous_unsubscribe_token.make_token(self.notification)
        return helpers.get_anonymous_unsubscribe_url(uidb64, token)

    def get_context_data(self):
        return super().get_context_data(
            company_list_url=settings.FAS_COMPANY_LIST_URL,
            utm_params=settings.NEW_COMPANIES_IN_SECTOR_UTM,
            companies=list(self.companies)[:5],  # show only 5: ED-1228
        )

    def send(self):
        with open('new-companies-in-sector.csv', 'w+') as csvfile:
            filewriter = csv.writer(csvfile)
            filewriter.writerow(
                [
                    'Name',
                    'Summary',
                    'Description',
                    'Number',
                    'Profile URL',
                ]
            )
            for company in self.companies:
                filewriter.writerow(
                    [
                        company.name,
                        company.summary,
                        company.description,
                        company.number,
                        settings.FAS_COMPANY_PROFILE_URL.format(number=company.number),
                    ]
                )

        with open('new-companies-in-sector.csv', 'rb') as f:
            notifications_client.send_email_notification(
                email_address=self.recipient.email,
                template_id=self.template_id,
                personalisation={
                    'link_to_file': prepare_upload(f),
                    'company_list_url': settings.FAS_COMPANY_LIST_URL,
                    'utm_params': settings.NEW_COMPANIES_IN_SECTOR_UTM,
                },
            )
        os.remove('new-companies-in-sector.csv')


class SupplierUbsubscribed(SupplierNotificationBase):
    html_template = 'unsubscribed-supplier.html'
    category = constants.UNSUBSCRIBED
    subject = settings.UNSUBSCRIBED_SUBJECT
    text_template = 'unsubscribed-supplier.txt'
    unsubscribe_url = None
    template_id = settings.GOVNOTIFY_ANONYMOUS_SUBSCRIBER_UNSUBSCRIBED_TEMPLATE_ID

    def send(self):
        notifications_client.send_email_notification(
            email_address=self.recipient.email,
            template_id=self.template_id,
            personalisation={
                'full_name': self.recipient.name,
                'zendesk_url': settings.ZENDESK_URL,
            },
        )


class AnonymousSubscriberUbsubscribed(AnonymousSubscriberNotificationBase):
    html_template = 'unsubscribed-anonymous-subscriber.html'
    category = constants.UNSUBSCRIBED
    subject = settings.UNSUBSCRIBED_SUBJECT
    text_template = 'unsubscribed-anonymous-subscriber.txt'
    unsubscribe_url = None
    template_id = settings.GOVNOTIFY_ANONYMOUS_SUBSCRIBER_UNSUBSCRIBED_TEMPLATE_ID

    def send(self):
        notifications_client.send_email_notification(
            email_address=self.recipient.email,
            template_id=self.template_id,
            personalisation={
                'full_name': self.recipient.name,
                'zendesk_url': settings.ZENDESK_URL,
            },
        )
