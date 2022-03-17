from django.conf import settings
from django.template.loader import render_to_string

from core.helpers import notifications_client


class MultiUserOwnershipBaseNotification:
    from_email = settings.FAB_FROM_EMAIL

    def __init__(self, instance):
        self.instance = instance

    @property
    def subject(self):
        return self.instance.subject

    def get_context_data(self, **kwargs):
        return {
            'invite_link': self.instance.invite_link,
            'requestor': (self.instance.requestor.name or self.instance.requestor.company_email),
            'company_name': self.instance.company.name,
        }

    def get_bodies(self):
        context = self.get_context_data()
        text_body = render_to_string(self.text_template, context)
        html_body = render_to_string(self.html_template, context)
        return text_body, html_body


class OwnershipChangeNotification(MultiUserOwnershipBaseNotification):
    template_id = settings.GOVNOTIFY_ACCOUNT_OWNERSHIP_TRANSFER_TEMPLATE_ID

    def send_async(self):
        notifications_client.send_email_notification(
            email_address=self.recipient.email,
            template_id=self.template_id,
            personalisation={
                'invite_link': self.instance.invite_link,
                'requestor': (self.instance.requestor.name or self.instance.requestor.company_email),
                'company_name': self.instance.company.name,
            },
        )


class CollaboratorNotification(MultiUserOwnershipBaseNotification):
    html_template = 'account_collaborator_email.html'
    text_template = 'account_collaborator_email.txt'

    def send_async(self):
        notifications_client.send_email_notification(
            email_address=self.recipient.email,
            template_id=self.template_id,
            personalisation={
                'invite_link': self.instance.invite_link,
                'requestor': (self.instance.requestor.name or self.instance.requestor.company_email),
                'company_name': self.instance.company.name,
            },
        )
