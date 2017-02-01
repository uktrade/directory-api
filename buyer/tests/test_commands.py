from unittest.mock import patch, Mock

import pytest

from zenpy.lib.api_objects import Ticket, User

from django.core.management import call_command

from buyer.tests.factories import BuyerFactory


@pytest.mark.django_db
@patch('buyer.management.commands.comments_to_zendesk.ZENPY_CLIENT.search')
@patch('zenpy.lib.api.UserApi.create')
@patch('zenpy.lib.api.TicketApi.create')
def test_doesnt_send_anything_for_buyers_without_comments(
    mock_ticket_create, mock_user_create, mock_search,
):
    BuyerFactory(comment='')

    call_command('comments_to_zendesk')

    assert mock_ticket_create.called is False
    assert mock_user_create.called is False
    assert mock_search.called is False


@pytest.mark.django_db
@patch('buyer.management.commands.comments_to_zendesk.ZENPY_CLIENT.search')
@patch('zenpy.lib.api.UserApi.create')
@patch('zenpy.lib.api.TicketApi.create')
def test_creates_user_and_ticket(
    mock_ticket_create, mock_user_create, mock_search,
):
    buyer = BuyerFactory()
    mock_user_create.return_value = Mock(id=123)
    mock_search.return_value = Mock(count=0, values=[])

    call_command('comments_to_zendesk')

    mock_search.assert_called_once_with(type='user')
    assert mock_user_create.call_count == 1
    user = mock_user_create.call_args[0][0]
    assert user.__class__ == User
    assert user.email == buyer.email
    assert user.name == buyer.name

    assert mock_ticket_create.call_count == 1
    ticket = mock_ticket_create.call_args[0][0]
    assert ticket.__class__ == Ticket
    assert ticket.subject == 'Trade Profiles feedback'
    assert ticket.submitter_id == 123
    assert ticket.requester_id == 123
    description = (
        'Name: {name}\n'
        'Email: {email}\n'
        'Company: {company_name}\n'
        'Country: {country}\n'
        'Sector: {sector}\n'
        'Comment: {comment}'
    ).format(
        name=buyer.name, email=buyer.email, sector=buyer.sector,
        company_name=buyer.company_name, country=buyer.country,
        comment=buyer.comment)
    assert ticket.description == description


@pytest.mark.django_db
@patch('buyer.management.commands.comments_to_zendesk.ZENPY_CLIENT.search')
@patch('zenpy.lib.api.UserApi.create')
@patch('zenpy.lib.api.TicketApi.create')
def test_creates_ticket_and_no_user_if_user_exists(
    mock_ticket_create, mock_user_create, mock_search,
):
    buyer = BuyerFactory()
    mock_search.return_value = Mock(
        count=1,
        values=[{
            'email': buyer.email,
            'name': buyer.name,
            'id': 521,
        }]
    )

    call_command('comments_to_zendesk')

    mock_search.assert_called_once_with(type='user')
    assert mock_user_create.called is False

    assert mock_ticket_create.call_count == 1
    ticket = mock_ticket_create.call_args[0][0]
    assert ticket.__class__ == Ticket
    assert ticket.subject == 'Trade Profiles feedback'
    assert ticket.submitter_id == 521
    assert ticket.requester_id == 521
    description = (
        'Name: {name}\n'
        'Email: {email}\n'
        'Company: {company_name}\n'
        'Country: {country}\n'
        'Sector: {sector}\n'
        'Comment: {comment}'
    ).format(
        name=buyer.name, email=buyer.email, sector=buyer.sector,
        company_name=buyer.company_name, country=buyer.country,
        comment=buyer.comment)
    assert ticket.description == description


@pytest.mark.django_db
@patch('buyer.management.commands.comments_to_zendesk.ZENPY_CLIENT.search')
@patch('zenpy.lib.api.UserApi.create')
@patch('zenpy.lib.api.TicketApi.create')
def test_correct_number_of_calls_to_zendesk_with_multiple_buyer_records(
    mock_ticket_create, mock_user_create, mock_search,
):
    BuyerFactory.create_batch(5, comment='')  # no calls for these
    buyers = BuyerFactory.create_batch(5)
    # Mock so two buyers are already in zendesk
    mock_search.return_value = Mock(
        count=2,
        values=[
            {
                'email': buyers[0].email,
                'name': buyers[0].name,
                'id': 523,
            },
            {
                'email': buyers[3].email,
                'name': buyers[3].name,
                'id': 674,
            },
        ]
    )

    call_command('comments_to_zendesk')

    assert mock_search.call_count == 1
    assert mock_user_create.call_count == 3
    assert mock_ticket_create.call_count == 5
