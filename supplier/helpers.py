from django.conf import settings

from directory_sso_api_client.client import DirectorySSOAPIClient


sso_api_client = DirectorySSOAPIClient(
    base_url=settings.SSO_API_CLIENT_BASE_URL,
    api_key=settings.SSO_SIGNATURE_SECRET,
)
