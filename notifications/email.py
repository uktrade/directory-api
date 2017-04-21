import abc

from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.template.loader import render_to_string

from notifications import constants, helpers, models


class Recipient:

    def __init__(self, name, email):
        self.email = email
        self.name = name


class NotificationBase(abc.ABC):
    html_template = None
    category = None
    recipient = None
    subject = None
    text_template = None
    unsubscribe_url = None
    zendesk_url = settings.ZENDESK_URL
    from_email = None

    def get_context_data(self, **kwargs):
        return {
            'full_name': self.recipient.name,
            'zendesk_url': self.zendesk_url,
            'unsubscribe_url': self.get_unsubscribe_url(),
            **kwargs
        }

    def get_unsubscribe_url(self):
        return self.unsubscribe_url

    def send(self):
        context = self.get_context_data()
        text_body = render_to_string(self.text_template, context)
        html_body = render_to_string(self.html_template, context)
        message = EmailMultiAlternatives(
            subject=self.subject,
            body=text_body,
            to=[self.recipient.email],
            from_email=self.from_email,
        )
        message.attach_alternative(html_body, "text/html")
        message.send()
        self.record_sent()

    @abc.abstractproperty
    def recipient(self):
        pass

    @abc.abstractmethod
    def record_sent(self):
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

    def record_sent(self):
        return models.SupplierEmailNotification.objects.create(
            supplier=self.supplier, category=self.category,
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

    def record_sent(self):
        return models.AnonymousEmailNotification.objects.create(
            email=self.recipient.email, category=self.category,
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

    def get_unsubscribe_url(self):
        return helpers.get_anonymous_unsubscribe_url(self.recipient.email)

    def get_context_data(self):
        return super().get_context_data(
            company_list_url=settings.FAS_COMPANY_LIST_URL,
            utm_params=settings.NEW_COMPANIES_IN_SECTOR_UTM,
            companies=self.companies,
        )
