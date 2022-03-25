from django.conf import settings

from core.helpers import notifications_client


class MultiUserOwnershipBaseNotification:
    from_email = settings.FAB_FROM_EMAIL

    def __init__(self, instance):
        self.instance = instance


class OwnershipChangeNotification(MultiUserOwnershipBaseNotification):
    template_id = settings.GOVNOTIFY_ACCOUNT_OWNERSHIP_TRANSFER_TEMPLATE_ID

    def send_async(self):
        notifications_client().send_email_notification(
            email_address=self.instance.recipient_email,
            template_id=self.template_id,
            personalisation={
                'invite_link': self.instance.invite_link,
                'requestor': (self.instance.requestor.name or self.instance.requestor.company_email),
                'company_name': self.instance.company.name,
            },
        )


class CollaboratorNotification(MultiUserOwnershipBaseNotification):
    template_id = settings.GOVNOTIFY_ACCOUNT_COLLABORATOR_TEMPLATE_ID

    def send_async(self):
        notifications_client().send_email_notification(
            email_address=self.instance.recipient_email,
            template_id=self.template_id,
            personalisation={
                'invite_link': self.instance.invite_link,
                'requestor': (self.instance.requestor.name or self.instance.requestor.company_email),
                'company_name': self.instance.company.name,
            },
        )
