import datetime
from unittest import mock

from directory_constants import company_types
import elasticsearch
from freezegun import freeze_time
import pytest

from django.utils import timezone

from company import documents, models
from company.tests import factories
from directory_constants import user_roles


@pytest.fixture(autouse=False)
def non_registration_sent_company():
    return factories.CompanyFactory(
        id=100000000,
        company_type=company_types.COMPANIES_HOUSE
    )


@pytest.mark.django_db
def test_does_not_overwrite_verification_code_if_already_set():
    with mock.patch('requests.post'):
        company = factories.CompanyFactory(verification_code='test')

    company.refresh_from_db()
    assert company.verification_code == 'test'


@pytest.mark.django_db
@mock.patch('company.helpers.send_verification_letter')
def test_does_not_send_verification_if_letter_already_sent(mock_send_letter):
    factories.CompanyFactory(
        is_verification_letter_sent=True,
        verification_code='test',
    )

    mock_send_letter.assert_not_called()


@pytest.mark.django_db
@freeze_time()
@mock.patch('company.helpers.send_verification_letter')
def test_letter_sent(mock_send_letter, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    company = factories.CompanyFactory(verification_code='test')

    assert mock_send_letter.call_count == 1
    assert mock_send_letter.call_args == mock.call(
        company=company,
        form_url='send_first_verification_letter'
    )


@pytest.mark.django_db
@mock.patch('company.helpers.send_verification_letter')
@mock.patch(
    'company.models.Company.has_valid_address',
    mock.Mock(return_value=False)
)
def test_unknown_address_not_send_letters(mock_send_letter):
    factories.CompanyFactory()

    mock_send_letter.send_letter.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize('is_publishable,is_published,expected', [
    [True, True, True],
    [True, False, False],
    [False, False, False],
    [False, True, True],

])
def test_publish(is_publishable, is_published, expected, settings):
    company = factories.CompanyFactory.build(is_published_find_a_supplier=is_published)

    mock_publishable = mock.PropertyMock(return_value=is_publishable)

    with mock.patch.object(models.Company, 'is_publishable', mock_publishable):
        company.save()
    assert company.is_published_find_a_supplier is expected


@pytest.mark.django_db
def test_store_date_published_unpublished_company():
    company = factories.CompanyFactory(is_published_find_a_supplier=False,)

    assert company.date_published is None


@pytest.mark.django_db
@freeze_time()
def test_store_date_published_published_company_isd_without_date():
    company = factories.CompanyFactory(
        is_published_find_a_supplier=True,
        date_published=None
    )

    assert company.date_published == timezone.now()


@pytest.mark.django_db
@freeze_time()
def test_store_date_published_published_company_fab_without_date():
    company = factories.CompanyFactory(
        is_published_find_a_supplier=True,
        date_published=None
    )

    assert company.date_published == timezone.now()


@pytest.mark.django_db
def test_store_date_published_published_isd_company_with_date():
    expected_date = timezone.now()

    company = factories.CompanyFactory(
        is_published_find_a_supplier=True,
        date_published=expected_date
    )

    assert company.date_published == expected_date


@pytest.mark.django_db
def test_store_date_published_published_fab_company_with_date():
    expected_date = timezone.now()

    company = factories.CompanyFactory(
        is_published_find_a_supplier=True,
        date_published=expected_date
    )

    assert company.date_published == expected_date


@pytest.mark.django_db
@pytest.mark.parametrize('is_published_find_a_supplier,' 'call_count', [(False, 0), (True, 1)])
def test_save_company_changes_to_elasticsearch(
    is_published_find_a_supplier, call_count, mock_elasticsearch_company_save
):
    factories.CompanyFactory(is_published_find_a_supplier=is_published_find_a_supplier)

    assert mock_elasticsearch_company_save.call_count == call_count


@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
def test_delete_company_from_elasticsearch():
    company = factories.CompanyFactory(
        is_published_find_a_supplier=True
    )
    company_pk = company.pk

    documents.CompanyDocument.get(id=company_pk)  # not raises if exists

    company.delete()

    with pytest.raises(elasticsearch.exceptions.NotFoundError):
        documents.CompanyDocument.get(id=company_pk)


@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
def test_delete_unpublished_isd_company_from_elasticsearch():
    company = factories.CompanyFactory(
        is_published_find_a_supplier=False
    )
    company_pk = company.pk

    company.delete()

    with pytest.raises(elasticsearch.exceptions.NotFoundError):
        documents.CompanyDocument.get(id=company_pk)


@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
def test_delete_unpublish_isd_company_from_elasticsearch():
    company = factories.CompanyFactory(
        is_published_find_a_supplier=True
    )
    company_pk = company.pk

    documents.CompanyDocument.get(id=company_pk)  # not raises if exists

    company.is_published_find_a_supplier = False
    company.save()

    with pytest.raises(elasticsearch.exceptions.NotFoundError):
        documents.CompanyDocument.get(id=company_pk)


@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
def test_delete_unpublished_fab_company_from_elasticsearch():
    company = factories.CompanyFactory(
        is_published_find_a_supplier=False
    )
    company_pk = company.pk

    company.delete()

    with pytest.raises(elasticsearch.exceptions.NotFoundError):
        documents.CompanyDocument.get(id=company_pk)


@pytest.mark.rebuild_elasticsearch
@pytest.mark.django_db
def test_delete_unpublish_fab_company_from_elasticsearch():
    company = factories.CompanyFactory(
        is_published_find_a_supplier=True
    )
    company_pk = company.pk

    documents.CompanyDocument.get(id=company_pk)  # not raises if exists

    company.is_published_find_a_supplier = False
    company.save()

    with pytest.raises(elasticsearch.exceptions.NotFoundError):
        documents.CompanyDocument.get(id=company_pk)


@pytest.mark.django_db
@mock.patch('company.helpers.send_new_user_invite_email')
def test_send_new_invite_collaboration_notification(mock_send_invite_email):
    collaboration_invite = factories.CollaborationInviteFactory()
    assert mock_send_invite_email.call_count == 1
    assert mock_send_invite_email.call_args == mock.call(
        collaboration_invite=collaboration_invite,
        form_url='send_new_invite_collaborator_notification',
    )

    collaboration_invite.accepted = True
    collaboration_invite.save()

    assert mock_send_invite_email.call_count == 1


@pytest.mark.django_db
@mock.patch('company.helpers.send_new_user_invite_email_existing_company')
def test_send_new_invite_collaboration_notification_existing_company(mock_send_invite_email):
    existing_member = factories.CompanyUserFactory()

    collaboration_invite = factories.CollaborationInviteFactory(
        collaborator_email=existing_member.company_email,
        company_user__company_email='test@test.com',
    )
    assert mock_send_invite_email.call_count == 1
    assert mock_send_invite_email.call_args == mock.call(
        collaboration_invite=collaboration_invite,
        existing_company_name=existing_member.company.name,
        form_url='send_new_invite_collaborator_notification_existing',
    )

    collaboration_invite.accepted = True
    collaboration_invite.save()

    assert mock_send_invite_email.call_count == 1


@pytest.mark.django_db
@mock.patch('company.helpers.send_new_user_alert_invite_accepted_email')
def test_send_acknowledgement_admin_email_on_invite_accept(mock_send_invite_accepted_email):
    collaboration_invite = factories.CollaborationInviteFactory()
    factories.CompanyUserFactory.create(company_email=collaboration_invite.collaborator_email, name='myname')

    assert mock_send_invite_accepted_email.call_count == 0
    collaboration_invite.accepted = True
    collaboration_invite.accepted_date = datetime.date.today()
    collaboration_invite.save()
    assert mock_send_invite_accepted_email.call_count == 1
    assert mock_send_invite_accepted_email.call_args == mock.call(
        collaboration_invite=collaboration_invite,
        collaborator_name='myname',
        form_url='send_acknowledgement_admin_email_on_invite_accept',
    )


@pytest.mark.django_db
@mock.patch('company.helpers.send_new_user_alert_invite_accepted_email')
def test_send_acknowledgement_admin_email_on_invite_reject(mock_send_invite_accepted_email):
    collaboration_invite = factories.CollaborationInviteFactory()
    factories.CompanyUserFactory.create(company_email=collaboration_invite.collaborator_email, name='myname')

    assert mock_send_invite_accepted_email.call_count == 0
    collaboration_invite.accepted = True
    collaboration_invite.accepted_date = datetime.date.today()
    collaboration_invite.save()
    assert mock_send_invite_accepted_email.call_count == 1
    assert mock_send_invite_accepted_email.call_args == mock.call(
        collaboration_invite=collaboration_invite,
        collaborator_name='myname',
        form_url='send_acknowledgement_admin_email_on_invite_accept',
    )


@pytest.mark.django_db
@mock.patch('company.helpers.send_new_user_alert_invite_accepted_email')
def test_send_acknowledgement_admin_email_on_invite_accept_modified(mock_send_invite_accepted_email):
    collaboration_invite = factories.CollaborationInviteFactory()

    assert mock_send_invite_accepted_email.call_count == 0
    collaboration_invite.accepted = False
    collaboration_invite.save()

    collaboration_invite.accepted = True
    collaboration_invite.save()
    assert mock_send_invite_accepted_email.call_count == 1

    collaboration_invite.collaborator_email = 'change@nochance.com'
    collaboration_invite.save()
    assert mock_send_invite_accepted_email.call_count == 1


@pytest.mark.django_db
@mock.patch('company.helpers.send_new_user_alert_invite_accepted_email')
def test_send_acknowledgement_admin_email_on_invite_accept_delete(mock_send_invite_accepted_email):
    collaboration_invite = factories.CollaborationInviteFactory()
    collaboration_invite.delete()

    assert mock_send_invite_accepted_email.call_count == 0


@pytest.mark.django_db
def test_set_companies_house_number():
    company = factories.CompanyFactory(company_type=company_types.COMPANIES_HOUSE, number=10101010)
    assert company.number == 10101010


@pytest.mark.parametrize(
    'company_type, '
    'company_prefix, ',
    [
        [company_types.SOLE_TRADER, 'ST'],
        [company_types.PARTNERSHIP, 'LP'],
        [company_types.CHARITY, 'CE'],
        ['OTHER', 'OT'],
    ]
)
@pytest.mark.django_db
def test_set_non_companies_house_number(company_type, company_prefix, settings):

    company = factories.CompanyFactory(company_type=company_type)

    seed = settings.SOLE_TRADER_NUMBER_SEED + 1

    assert company.number == f'{company_prefix}{seed:06}'


@pytest.mark.django_db
@mock.patch('company.helpers.send_registration_letter')
def test_does_not_send_verification_if_created_before_feature(
        mock_send_letter, non_registration_sent_company, settings):
    settings.FEATURE_REGISTRATION_LETTERS_ENABLED = True

    with freeze_time('2017-01-14 12:00:01'):
        factories.CompanyUserFactory(
            company=non_registration_sent_company
        )
    mock_send_letter.assert_not_called()


@pytest.mark.django_db
@mock.patch('company.helpers.send_registration_letter')
def test_send_verification_if_created_after_feature(mock_send_letter, non_registration_sent_company, settings):
    settings.FEATURE_REGISTRATION_LETTERS_ENABLED = True

    with freeze_time('2019-12-12 12:00:01'):
        factories.CompanyUserFactory(
            company=non_registration_sent_company
        )
    mock_send_letter.call_count = 1


@pytest.mark.django_db
@mock.patch('company.helpers.send_user_collaboration_request_declined_email')
def test_user_send_collaboration_request_email_on_decline(mock_send_email):
    collaboration_request = factories.CollaborationRequestFactory()
    collaboration_request.delete()
    mock_send_email.call_args = mock.call(
        collaboration_request=collaboration_request, form_url='send_user_collaboration_request_email_on_decline'
    )


@pytest.mark.django_db
@mock.patch('company.helpers.send_admins_new_collaboration_request_email')
def test_send_admins_new_collaboration_request_notification(mock_send_email):

    company = factories.CompanyFactory()
    factories.CompanyUserFactory(company=company, role=user_roles.ADMIN)
    factories.CompanyUserFactory(company=company, role=user_roles.ADMIN)
    member_user = factories.CompanyUserFactory(company=company, role=user_roles.MEMBER)

    admins = models.CompanyUser.objects.filter(company_id=company.id, role=user_roles.ADMIN)

    collaboration_request = factories.CollaborationRequestFactory(requestor=member_user)

    mock_send_email.call_args = mock.call(
        company_admins=admins,
        collaboration_request=collaboration_request,
        form_url='send_admins_new_collaboration_request_email'
    )


@pytest.mark.django_db
@mock.patch('company.helpers.send_admins_new_collaboration_request_email')
def test_send_admins_new_collaboration_request_notification_not_sent_modify(mock_send_email):
    colloboration_request = factories.CollaborationRequestFactory()
    colloboration_request.name = 'xyz'
    colloboration_request.save()
    mock_send_email.call_count = 1


@pytest.mark.django_db
@mock.patch('company.helpers.send_user_collaboration_request_declined_email')
def test_user_send_collaboration_request_email_on_decline_not_sent_when_accepted(mock_send_email):
    collaboration_request = factories.CollaborationRequestFactory(accepted=True)
    collaboration_request.delete()
    mock_send_email.assert_not_called()


@pytest.mark.django_db
@mock.patch('company.helpers.send_user_collaboration_request_accepted_email')
def test_user_send_collaboration_request_email_on_accept(mock_send_email):
    collaboration_request = factories.CollaborationRequestFactory()
    collaboration_request.accepted = True
    collaboration_request.save()
    mock_send_email.call_args = mock.call(
        collaboration_request=collaboration_request, form_url='send_user_collaboration_request_email_on_accept'
    )


@pytest.mark.django_db
@mock.patch('company.helpers.send_user_collaboration_request_accepted_email')
def test_user_send_collaboration_request_email_on_accept_not_sent_on_modified(mock_send_email):
    collaboration_request = factories.CollaborationRequestFactory()
    collaboration_request.name = 'xyz'
    collaboration_request.save()
    mock_send_email.assert_not_called()
