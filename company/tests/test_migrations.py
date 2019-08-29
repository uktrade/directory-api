import pytest

from directory_constants import user_roles


@pytest.mark.django_db
def test_populate_products_services(migration):
    historic_apps = migration.before([('company', '0089_auto_20190829_0845')])

    Company = historic_apps.get_model('company', 'Company')
    Supplier = historic_apps.get_model('supplier', 'Supplier')
    CollaboratorInvite = historic_apps.get_model('company', 'CollaboratorInvite')
    OwnershipInvite = historic_apps.get_model('company', 'OwnershipInvite')

    company = Company.objects.create(
        name='private company',
        website='http://example.com',
        description='Company description',
        has_exported_before=True,
        date_of_creation='2010-10-10',
        email_address='thing@example.com',
        verified_with_code=True,
    )
    supplier = Supplier.objects.create(
        company=company,
        sso_id=1,
        name='jim example',
        company_email='jim@example.com',
    )

    collaborator_invite = CollaboratorInvite.objects.create(
        uuid='2327f510-3291-4aa1-8d75-3b78e50377a6',
        collaborator_email='collaborator@example.com',
        company=company,
        requestor=supplier,
    )
    ownership_invite = OwnershipInvite.objects.create(
        uuid='2327f510-3291-4aa1-8d75-3b78e50377a2',
        new_owner_email='owner@example.com',
        company=company,
        requestor=supplier,
    )

    apps = migration.apply('company', '0090_auto_20190829_0845')
    CollaborationInvite = apps.get_model('company', 'CollaborationInvite')

    assert CollaborationInvite.objects.count() == 2
    invite_one = CollaborationInvite.objects.get(uuid=collaborator_invite.uuid)
    assert invite_one.collaborator_email == collaborator_invite.collaborator_email
    assert invite_one.company.pk == collaborator_invite.company.pk
    assert invite_one.requestor.pk == collaborator_invite.requestor.pk
    assert invite_one.role == user_roles.EDITOR

    invite_two = CollaborationInvite.objects.get(uuid=ownership_invite.uuid)
    assert invite_two.collaborator_email == ownership_invite.new_owner_email
    assert invite_two.company.pk == ownership_invite.company.pk
    assert invite_two.requestor.pk == ownership_invite.requestor.pk
    assert invite_two.role == user_roles.ADMIN
