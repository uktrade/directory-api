from django.conf import settings
from django.core.management.base import BaseCommand

from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket, User

from buyer.models import Buyer


ZENPY_CREDENTIALS = {
    'email': settings.ZENDESK_EMAIL,
    'token': settings.ZENDESK_TOKEN,
    'subdomain': settings.ZENDESK_SUBDOMAIN
}
# Zenpy will let the connection timeout after 5s and will retry 3 times
ZENPY_CLIENT = Zenpy(timeout=5, **ZENPY_CREDENTIALS)


class Command(BaseCommand):
    help = 'Sends data in the Buyer.comments field to zendesk'

    def _create_zendesk_ticket(self, buyer):
        if buyer.email not in self.existing_users:
            user = User(name=buyer.name, email=buyer.email)
            user_id = ZENPY_CLIENT.users.create(user).id
        else:
            user_id = self.existing_users[buyer.email]

        description = (
            'Name: {name}\n'
            'Email: {email}\n'
            'Company: {company_name}\n'
            'Country: {country}\n'
            'Sector: {sector}\n'
            'Comment: {comment}'
        ).format(
            name=buyer.name,
            email=buyer.email,
            company_name=buyer.company_name,
            country=buyer.country,
            sector=buyer.sector,
            comment=buyer.comment,
        )
        ticket = Ticket(
            subject=settings.ZENDESK_TICKET_SUBJECT,
            description=description,
            submitter_id=user_id,
            requester_id=user_id,
        )
        ZENPY_CLIENT.tickets.create(ticket)

    def handle(self, *args, **options):
        buyers = Buyer.objects.exclude(comment='')
        if not buyers:
            self.stdout.write(
                'No buyers with comments in db. Nothing to send to '
                'zendesk'
            )
            return

        self.existing_users = {
            user['email']: user['id']
            for user in ZENPY_CLIENT.search(type='user').values
        }
        for buyer in buyers:
            self._create_zendesk_ticket(buyer)
