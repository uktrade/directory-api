import abc
from collections import namedtuple

from django.conf import settings
from django.template.loader import render_to_string

from notifications import constants, helpers, tasks, models


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
            **kwargs
        }

    def get_bodies(self):
        context = self.get_context_data()
        text_body = render_to_string(self.text_template, context)
        html_body = render_to_string(self.html_template, context)
        return text_body, html_body

    def send(self):
        pass


class SupplierNotificationBase(NotificationBase):
    from_email = settings.FAB_FROM_EMAIL

    def __init__(self, supplier):
        self.supplier = supplier

    @property
    def recipient(self):
        return Recipient(
            name=self.supplier.name,
            email=self.supplier.company_email
        )

    def send(self):
        text_body, html_body = self.get_bodies()
        models.SupplierEmailNotification.objects.create(
            supplier=self.supplier,
            category=self.category
        )
        tasks.send_email.delay(
            subject=self.subject,
            text_body=text_body,
            html_body=html_body,
            recipient_email=self.recipient.email,
            from_email=self.from_email,
        )


class AnonymousSubscriberNotificationBase(NotificationBase):
    from_email = settings.FAS_FROM_EMAIL

    def __init__(self, subscriber):
        self.subscriber = subscriber

    @property
    def recipient(self):
        return Recipient(
            name=self.subscriber['name'],
            email=self.subscriber['email']
        )

    def send(self):
        text_body, html_body = self.get_bodies()
        models.AnonymousEmailNotification.objects.create(
            email=self.recipient.email, category=self.category
        )
        tasks.send_email.delay(
            subject=self.subject,
            text_body=text_body,
            html_body=html_body,
            recipient_email=self.recipient.email,
            from_email=self.from_email
        )


class NoCaseStudiesNotification(SupplierNotificationBase):
    html_template = 'no_case_studies_email.html'
    category = constants.NO_CASE_STUDIES
    subject = settings.NO_CASE_STUDIES_SUBJECT
    text_template = 'no_case_studies_email.txt'
    unsubscribe_url = settings.FAB_NOTIFICATIONS_UNSUBSCRIBE_URL

    def get_context_data(self):
        return super().get_context_data(
            case_study_url=settings.NO_CASE_STUDIES_URL,
            utm_params=settings.NO_CASE_STUDIES_UTM,
        )


class HasNotLoggedInRecentlyNotification(SupplierNotificationBase):
    html_template = 'hasnt_logged_in_email.html'
    category = constants.HASNT_LOGGED_IN
    subject = settings.HASNT_LOGGED_IN_SUBJECT
    text_template = 'hasnt_logged_in_email.txt'
    unsubscribe_url = settings.FAB_NOTIFICATIONS_UNSUBSCRIBE_URL

    def get_context_data(self):
        return super().get_context_data(
            login_url=settings.HASNT_LOGGED_IN_URL,
            utm_params=settings.HASNT_LOGGED_IN_UTM,
        )


class VerificationWaitingNotification(SupplierNotificationBase):
    html_template = 'verification_code_not_given_email.html'
    category = constants.VERIFICATION_CODE_NOT_GIVEN
    subject = settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT
    text_template = 'verification_code_not_given_email.txt'
    unsubscribe_url = settings.FAB_NOTIFICATIONS_UNSUBSCRIBE_URL

    def get_context_data(self):
        return super().get_context_data(
            verification_url=settings.VERIFICATION_CODE_URL,
        )


class VerificationStillWaitingNotification(SupplierNotificationBase):
    html_template = 'verification_code_not_given_2nd_email.html'
    category = constants.VERIFICATION_CODE_2ND_EMAIL
    subject = settings.VERIFICATION_CODE_NOT_GIVEN_SUBJECT_2ND_EMAIL
    text_template = 'verification_code_not_given_2nd_email.txt'
    unsubscribe_url = settings.FAB_NOTIFICATIONS_UNSUBSCRIBE_URL

    def get_context_data(self):
        return super().get_context_data(
            verification_url=settings.VERIFICATION_CODE_URL,
        )


class NewCompaniesInSectorNotification(AnonymousSubscriberNotificationBase):
    html_template = 'new_companies_in_sector_email.html'
    category = constants.NEW_COMPANIES_IN_SECTOR
    subject = settings.NEW_COMPANIES_IN_SECTOR_SUBJECT
    text_template = 'new_companies_in_sector_email.txt'

    def __init__(self, subscriber, companies):
        self.companies = companies
        super().__init__(subscriber=subscriber)

    @property
    def unsubscribe_url(self):
        return helpers.get_anonymous_unsubscribe_url(self.recipient.email)

    def get_context_data(self):
        return super().get_context_data(
            company_list_url=settings.FAS_COMPANY_LIST_URL,
            utm_params=settings.NEW_COMPANIES_IN_SECTOR_UTM,
            companies=list(self.companies)[:5],  # show only 5: ED-1228
        )


class SupplierUbsubscribed(SupplierNotificationBase):
    html_template = 'unsubscribed-supplier.html'
    category = constants.UNSUBSCRIBED
    subject = settings.UNSUBSCRIBED_SUBJECT
    text_template = 'unsubscribed-supplier.txt'
    unsubscribe_url = None


class AnonymousSubscriberUbsubscribed(AnonymousSubscriberNotificationBase):
    html_template = 'unsubscribed-anonymous-subscriber.html'
    category = constants.UNSUBSCRIBED
    subject = settings.UNSUBSCRIBED_SUBJECT
    text_template = 'unsubscribed-anonymous-subscriber.txt'
    unsubscribe_url = None


class MultiUserOwnershipBaseNotification(NotificationBase):
    from_email = settings.FAB_FROM_EMAIL
    category = None
    unsubscribe_url = None

    def __init__(self, instance):
        self.instance = instance

    @property
    def subject(self):
        return self.instance.subject

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            invite_link=self.instance.invite_link,
            requestor_name=self.instance.requestor.name,
            company_name=self.instance.company.name
        )

    def send(self):
        text_body, html_body = self.get_bodies()
        tasks.send_email.delay(
            subject=self.instance.subject,
            text_body=text_body,
            html_body=html_body,
            recipient_email=self.instance.recipient_email,
            from_email=self.from_email,
        )


class OwnershipChangeNotification(MultiUserOwnershipBaseNotification):
    html_template = 'account_ownership_transfer_email.html'
    text_template = 'account_ownership_transfer_email.txt'


class CollaboratorNotification(MultiUserOwnershipBaseNotification):
    html_template = 'account_collaborator_email.html'
    text_template = 'account_collaborator_email.txt'
