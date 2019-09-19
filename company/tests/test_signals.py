import datetime
from unittest import mock

from directory_constants import company_types, user_roles
import elasticsearch
from freezegun import freeze_time
import pytest

from django.utils import timezone

from company import documents, models
from company.tests import factories
from supplier.tests.factories import SupplierFactory


@pytest.fixture(autouse=False)
def non_registration_sent_company():
    return factories.CompanyFactory(
        id=100000000,
        company_type=company_types.COMPANIES_HOUSE
    )


@pytest.mark.django_db
def test_sends_verification_letter_stannp_post_save(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post') as requests_mock:
        company = factories.CompanyFactory()

    company.refresh_from_db()
    assert company.verification_code

    requests_mock.assert_called_once_with(
        'https://dash.stannp.com/api/v1/letters/create',
        auth=('debug', ''),
        data={
            'test': True,
            'recipient[company_name]': company.name,
            'recipient[country]': company.country,
            'recipient[date]': datetime.date.today().strftime('%d/%m/%Y'),
            'recipient[address1]': company.address_line_1,
            'recipient[full_name]': company.postal_full_name,
            'recipient[city]': company.locality,
            'recipient[company]': company.name,
            'recipient[postcode]': company.postal_code,
            'recipient[title]': company.postal_full_name,
            'recipient[address2]': company.address_line_2,
            'recipient[verification_code]': company.verification_code,
            'template': 'debug'
        },
    )


@pytest.mark.django_db
@mock.patch('company.helpers.send_registration_letter')
def test_sends_registration_letter_post_save(
        mock_utils_send_registration_letter, settings
):
    settings.FEATURE_REGISTRATION_LETTERS_ENABLED = True
    company = factories.CompanyFactory()

    assert mock_utils_send_registration_letter.call_count == 1
    assert mock_utils_send_registration_letter.call_args == mock.call(
        company=company,
        form_url='send_company_claimed_letter_automatically_sent',
    )


@pytest.mark.parametrize(
    'letter_registration_enabled, '
    'is_registration_letter_sent, '
    'company_type, '
    'address_line_1, '
    'postal_code, ',
    [
        [False, True, company_types.COMPANIES_HOUSE, 'addr', 'N1 8NP'],
        [True,  True, company_types.COMPANIES_HOUSE, 'addr', 'N1 8NP'],
        [True,  True, company_types.CHARITY, 'addr', 'N1 8NP'],
        [True,  True, company_types.PARTNERSHIP, 'addr', 'N1 8NP'],
        [True,  True, company_types.SOLE_TRADER, 'addr', 'N1 8NP'],
        [True,  True,  company_types.COMPANIES_HOUSE, '', 'N1 8NP'],
        [True,  True,  company_types.COMPANIES_HOUSE, 'addr', ''],
    ]
)
@mock.patch('company.helpers.send_registration_letter')
@pytest.mark.django_db
def test_does_not_send_registration_letter_conditions(
        mock_utils_send_registration_letter,
        letter_registration_enabled,
        is_registration_letter_sent,
        company_type,
        address_line_1,
        postal_code,
        settings,
):

    settings.FEATURE_REGISTRATION_LETTERS_ENABLED = letter_registration_enabled
    company = factories.CompanyFactory(
        is_registration_letter_sent=is_registration_letter_sent,
        company_type=company_type,
        address_line_1=address_line_1,
        postal_code=postal_code,
    )
    assert mock_utils_send_registration_letter.call_count == 0
    company.refresh_from_db()

    assert company.is_verification_letter_sent is False
    assert company.date_verification_letter_sent is None


@pytest.mark.django_db
def test_does_not_send_verification_letter_on_update(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post') as requests_mock:
        company = factories.CompanyFactory(name="Original name")
        company.name = "Changed name"
        company.save()

    requests_mock.assert_called_once_with(
        'https://dash.stannp.com/api/v1/letters/create',
        auth=('debug', ''),
        data={
            'test': True,
            'recipient[company_name]': 'Original name',
            'recipient[country]': company.country,
            'recipient[date]': datetime.date.today().strftime('%d/%m/%Y'),
            'recipient[address1]': company.address_line_1,
            'recipient[full_name]': company.postal_full_name,
            'recipient[city]': company.locality,
            'recipient[company]': 'Original name',
            'recipient[postcode]': company.postal_code,
            'recipient[title]': company.postal_full_name,
            'recipient[address2]': company.address_line_2,
            'recipient[verification_code]': company.verification_code,
            'template': 'debug'
        },
    )


@pytest.mark.django_db
def test_does_not_overwrite_verification_code_if_already_set(settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True

    with mock.patch('requests.post'):
        company = factories.CompanyFactory(verification_code='test')

    company.refresh_from_db()
    assert company.verification_code == 'test'


@pytest.mark.django_db
@mock.patch('company.helpers.send_verification_letter')
def test_does_not_send_verification_if_letter_already_sent(
        mock_send_letter,
        settings
):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
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
def test_unknown_address_not_send_letters(mock_send_letter, settings):
    settings.FEATURE_VERIFICATION_LETTERS_ENABLED = True
    factories.CompanyFactory()

    mock_send_letter.send_letter.assert_not_called()


@pytest.mark.django_db
@pytest.mark.parametrize('enabled,is_publishable,is_published,expected', [
    [True, True, True, True],
    [True, True, False, False],
    [True, False, False, False],
    [True, False, True, True],
    [False, False, False, False],
    [False, False, True, True],
    [False, True, True, True],
    [False, True, False, True],
])
def test_publish(enabled, is_publishable, is_published, expected, settings):
    settings.FEATURE_MANUAL_PUBLISH_ENABLED = enabled

    company = factories.CompanyFactory.build(
        is_published_find_a_supplier=is_published
    )

    mock_publishable = mock.PropertyMock(return_value=is_publishable)

    with mock.patch.object(models.Company, 'is_publishable', mock_publishable):
        company.save()
    assert company.is_published_find_a_supplier is expected


@pytest.mark.django_db
def test_store_date_published_unpublished_company():
    company = factories.CompanyFactory(
        is_published_find_a_supplier=False,
    )

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
@pytest.mark.parametrize(
    'is_published_find_a_supplier,'
    'call_count',
    [
        (False, 0),
        (True, 1),
    ]
)
def test_save_company_changes_to_elasticsearch(
    is_published_find_a_supplier,
    call_count,
    mock_elasticsearch_company_save,
):
    factories.CompanyFactory(
        is_published_find_a_supplier=(
            is_published_find_a_supplier
        )
    )

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
@mock.patch('company.email.OwnershipChangeNotification')
def test_account_ownership_transfer_email_notification(mocked_notification):
    factories.OwnershipInviteFactory()
    assert mocked_notification().send_async.called is True


@pytest.mark.django_db
@mock.patch('company.email.CollaboratorNotification')
def test_account_collaborator_email_notification(mocked_notification):
    factories.CollaboratorInviteFactory()
    assert mocked_notification().send_async.called is True


@pytest.mark.django_db
@mock.patch('company.email.CollaboratorNotification')
def test_account_collaborator_email_notification_modified(mocked_notification):
    invite = factories.CollaboratorInviteFactory()

    # now modify it

    invite.accepted = True
    invite.save()

    assert mocked_notification().send_async.call_count == 1


@pytest.mark.django_db
def test_create_collaboration_invite_from_ownership_invite():
    invite = factories.OwnershipInviteFactory()

    collaboration_invite = models.CollaborationInvite.objects.get(uuid=invite.uuid)

    assert collaboration_invite.collaborator_email == invite.new_owner_email
    assert collaboration_invite.company.pk == invite.company.pk
    assert collaboration_invite.requestor.pk == invite.requestor.pk
    assert collaboration_invite.role == user_roles.ADMIN


@pytest.mark.django_db
def test_create_collaboration_invite_from_collaborator_invite():
    invite = factories.CollaboratorInviteFactory()

    collaboration_invite = models.CollaborationInvite.objects.get(uuid=invite.uuid)

    assert collaboration_invite.collaborator_email == invite.collaborator_email
    assert collaboration_invite.company.pk == invite.company.pk
    assert collaboration_invite.requestor.pk == invite.requestor.pk
    assert collaboration_invite.role == user_roles.EDITOR


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
    existing_member = SupplierFactory()

    collaboration_invite = factories.CollaborationInviteFactory(
        collaborator_email=existing_member.company_email,
        requestor__company_email='test@test.com',
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
@mock.patch('company.helpers.send_new_user_invite_email')
def test_send_new_invite_collaboration_notification_existing_supplier_only(mock_send_invite_email):
    existing_member = SupplierFactory(company=None)
    collaboration_invite = factories.CollaborationInviteFactory(
        collaborator_email=existing_member.company_email,
        requestor__company_email='test@test.com',
    )

    assert mock_send_invite_email.call_count == 1
    assert mock_send_invite_email.call_args == mock.call(
        collaboration_invite=collaboration_invite,
        form_url='send_new_invite_collaborator_notification',
    )



