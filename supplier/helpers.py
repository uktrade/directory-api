from django.conf import settings
from django.utils.functional import cached_property

from directory_sso_api_client.client import DirectorySSOAPIClient


from user.models import User as Supplier


sso_api_client = DirectorySSOAPIClient(
    base_url=settings.SSO_API_CLIENT_BASE_URL,
    api_key=settings.SSO_SIGNATURE_SECRET,
)


class SSOUser:
    def __init__(self, id, email):
        self.id = id
        self.email = email

    @cached_property
    def supplier(self):
        try:
            return Supplier.objects.get(sso_id=self.id)
        except Supplier.DoesNotExist:
            return None
