import pytest
from rest_framework import status
from rest_framework.reverse import reverse


@pytest.mark.django_db
def test_company_create_transfer_ownership_invite(
        authed_client,
        authed_supplier):

    data = {
        'new_owner_email': 'foo@bar.com',
        'company': authed_supplier.company.pk,
        'requestor': authed_supplier.pk,
    }
    response = authed_client.post(
        reverse('transfer-ownership-invite-create'),
        data,
        format='json'
    )

    assert response.status_code == status.HTTP_201_CREATED
