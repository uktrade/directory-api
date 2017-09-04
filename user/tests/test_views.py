import pytest
from rest_framework import status
from rest_framework.reverse import reverse

from user.models import OwnershipInvite


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
        data=data,
        format='json'
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == data
    assert OwnershipInvite.objects.filter(
        new_owner_email='foo@bar.com'
    ).exists()
