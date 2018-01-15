import pytest

from company.tests.helpers import (
    build_collaborator_invite_factory, build_ownership_invite_factory
)
from user.tests.helpers import build_user_factory
from company.tests.helpers import build_company_factory


@pytest.mark.django_db
def test_collaborator_invite_transfer_to_supplier(migration):

    historic_apps = migration.before([
        ('user', '0010_auto_20170907_1552'),
        ('company', '0068_auto_20171011_1307'),
        ('supplier', '0001_initial'),
    ])

    HistoricUserFactory = build_user_factory(
        historic_apps.get_model('user', 'User')
    )
    HistoricCollaboratorInviteFactory = build_collaborator_invite_factory(
        historic_apps.get_model('company', 'CollaboratorInvite')
    )
    HistoricCompanyFactory = build_company_factory(
        historic_apps.get_model('company', 'Company')
    )

    historic_user_one = HistoricUserFactory.create(
        company=HistoricCompanyFactory.create(),
    )
    historic_user_two = HistoricUserFactory.create(
        company=HistoricCompanyFactory.create(),
    )
    historic_collaborator_invite_one = HistoricCollaboratorInviteFactory(
        requestor=historic_user_one,
        company=historic_user_one.company,
    )
    historic_collaborator_invite_two = HistoricCollaboratorInviteFactory(
        requestor=historic_user_two,
        company=historic_user_two.company,
    )

    apps = migration.apply('company', '0069_auto_20180103_1719')
    Supplier = apps.get_model('supplier', 'Supplier')
    CollaboratorInvite = apps.get_model('company', 'CollaboratorInvite')

    pairs = (
        (historic_collaborator_invite_one, historic_user_one),
        (historic_collaborator_invite_two, historic_user_two),
    )

    for historic_invite, historic_user in pairs:
        invite = CollaboratorInvite.objects.get(pk=historic_invite.pk)
        supplier = Supplier.objects.get(pk=historic_user.pk)

        assert invite.requestor == supplier


@pytest.mark.django_db
def test_ownership_invite_transfer_to_supplier(migration):

    historic_apps = migration.before([
        ('user', '0010_auto_20170907_1552'),
        ('company', '0068_auto_20171011_1307'),
        ('supplier', '0001_initial'),
    ])

    HistoricUserFactory = build_user_factory(
        historic_apps.get_model('user', 'User')
    )
    HistoricOwnershipInviteFactory = build_ownership_invite_factory(
        historic_apps.get_model('company', 'OwnershipInvite')
    )
    HistoricCompanyFactory = build_company_factory(
        historic_apps.get_model('company', 'Company')
    )

    historic_user_one = HistoricUserFactory.create(
        company=HistoricCompanyFactory.create(),
    )
    historic_user_two = HistoricUserFactory.create(
        company=HistoricCompanyFactory.create(),
    )
    historic_ownership_invite_one = HistoricOwnershipInviteFactory(
        requestor=historic_user_one,
        company=historic_user_one.company,
    )
    historic_ownership_invite_two = HistoricOwnershipInviteFactory(
        requestor=historic_user_two,
        company=historic_user_two.company,
    )

    apps = migration.apply('company', '0069_auto_20180103_1719')
    Supplier = apps.get_model('supplier', 'Supplier')
    OwnershipInvite = apps.get_model('company', 'OwnershipInvite')

    pairs = (
        (historic_ownership_invite_one, historic_user_one),
        (historic_ownership_invite_two, historic_user_two),
    )

    for historic_invite, historic_user in pairs:
        invite = OwnershipInvite.objects.get(pk=historic_invite.pk)
        supplier = Supplier.objects.get(pk=historic_user.pk)

        assert invite.requestor == supplier
