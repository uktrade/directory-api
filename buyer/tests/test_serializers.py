import pytest
import json

from buyer import serializers
from buyer.tests.factories import BuyerFactory


@pytest.mark.django_db
def test_buyer_deserialization_create():
    data = {
        'email': 'jim@example.com',
        'name': 'Jim Exampleson',
        'sector': 'AEROSPACE',
        'sectors': json.dumps(['AEROSPACE']),
        'company_name': 'Example corp',
        'country': 'China',
    }

    serializer = serializers.BuyerSerializer(data=data)

    assert serializer.is_valid()
    instance = serializer.save()
    assert instance.email == data['email']
    assert instance.name == data['name']
    assert instance.sector == data['sector']
    assert instance.sectors == data['sectors']
    assert instance.company_name == data['company_name']
    assert instance.country == data['country']


@pytest.mark.django_db
def test_buyer_deserialization_update():
    data = {
        'email': 'jim@example.com',
        'name': 'Jim Exampleson',
        'sector': 'AEROSPACE',
        'sectors': json.dumps(['AEROSPACE', 'WATER']),
        'company_name': 'Example corp',
        'country': 'China',
    }
    buyer = BuyerFactory(
        email='jim@example.com',
        sectors=json.dumps(['MINING']),
    )

    serializer = serializers.BuyerSerializer(instance=buyer, data=data)

    assert serializer.is_valid()
    instance = serializer.save()
    assert instance.email == data['email']
    assert instance.name == data['name']
    assert instance.sector == data['sector']
    assert instance.sectors == ['MINING', 'AEROSPACE', 'WATER']
    assert instance.company_name == data['company_name']
    assert instance.country == data['country']
