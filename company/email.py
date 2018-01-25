from django.conf import settings
from django.template.loader import render_to_string

from core import tasks


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
            'requestor': (
                self.instance.requestor.name or
                self.instance.requestor.company_email
            ),
            'company_name': self.instance.company.name
        }

    def get_bodies(self):
        context = self.get_context_data()
        text_body = render_to_string(self.text_template, context)
        html_body = render_to_string(self.html_template, context)
        return text_body, html_body

    def send_async(self):
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
