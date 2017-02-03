import pytest

from buyer import serializers


@pytest.mark.django_db
def test_buyer_deserialization():
    data = {
        'email': 'jim@example.com',
        'name': 'Jim Exampleson',
        'sector': 'AEROSPACE',
        'company_name': 'Example corp',
        'country': 'China',
    }

    serializer = serializers.BuyerSerializer(data=data)

    assert serializer.is_valid()
    instance = serializer.save()
    assert instance.email == data['email']
    assert instance.name == data['name']
    assert instance.sector == data['sector']
    assert instance.company_name == data['company_name']
    assert instance.country == data['country']
