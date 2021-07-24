from unittest.mock import patch

import pytest

from personalisation import helpers, models


@patch('requests.get')
def test_exporting_is_great_handles_auth(mock_get, settings):
    client = helpers.ExportingIsGreatClient()
    client.base_url = 'http://b.co'
    client.secret = 123
    username = settings.EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_USERNAME
    password = settings.EXPORTING_OPPORTUNITIES_API_BASIC_AUTH_PASSWORD

    client.get_opportunities(2, '')

    mock_get.assert_called_once_with(
        'http://b.co/export-opportunities/api/opportunities',
        params={'hashed_sso_id': 2, 'shared_secret': 123, 's': ''},
        auth=helpers.exopps_client.auth,
    )
    assert helpers.exopps_client.auth.username == username
    assert helpers.exopps_client.auth.password == password


@pytest.mark.django_db
def test_get_business_user():
    business_user1 = helpers.get_business_user(6)
    assert len(models.BusinessUser.objects.all()) == 1
    business_user2 = helpers.get_business_user(6)
    assert len(models.BusinessUser.objects.all()) == 1
    assert business_user1 == business_user2


@pytest.mark.django_db
def test_create_or_update_product():
    product_data1 = {'commodity_git pushname': 'gin'}
    product_data2 = {'commodity_name': 'cheese'}

    helpers.create_or_update_product(user_id=1, user_product_data=product_data1)
    business_user = helpers.get_business_user(1)
    assert len(models.UserProduct.objects.all()) == 1
    assert models.UserProduct.objects.get(business_user=business_user).product_data == product_data1
    # Test temporary behaviour.  Adding a product, just updates the user's one existing one
    helpers.create_or_update_product(user_id=1, user_product_data=product_data2)
    assert len(models.UserProduct.objects.all()) == 1
    assert models.UserProduct.objects.get(business_user=business_user).product_data == product_data2


@pytest.mark.django_db
def test_create_or_update_market():
    market_data1 = {'market pushname': 'China', 'country_iso2_code': 'CN'}
    market_data2 = {'country_name': 'Netherlands', 'country_iso2_code': 'NL'}

    helpers.create_or_update_market(user_id=1, user_market_data=market_data1)
    business_user = helpers.get_business_user(1)
    assert len(models.UserMarket.objects.all()) == 1
    assert models.UserMarket.objects.get(business_user=business_user).data == market_data1
    # Test temporary behaviour.  Adding a market, just updates the user's one existing one
    helpers.create_or_update_market(user_id=1, user_market_data=market_data2)
    assert len(models.UserMarket.objects.all()) == 1
    assert models.UserMarket.objects.get(business_user=business_user).data == market_data2
    assert (
        models.UserMarket.objects.get(business_user=business_user).country_iso2_code
        == market_data2['country_iso2_code']
    )
