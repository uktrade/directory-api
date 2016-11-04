import pytest

from buyer import serializers


@pytest.mark.django_db
def test_buyer_deserialization():
    data = {
        'email': 'jim@example.com',
        'name': 'Jim Exampleson',
        'sector': 'AEROSPACE',
    }

    serializer = serializers.BuyerSerializer(data=data)

    assert serializer.is_valid()
    instance = serializer.save()
    assert instance.email == data['email']
    assert instance.name == data['name']
    assert instance.sector == data['sector']
