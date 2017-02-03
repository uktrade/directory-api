import pytest

from buyer import serializers
from buyer.tests.factories import BuyerFactory


@pytest.mark.django_db
def test_buyer_deserialization():
    data = BuyerFactory.stub().__dict__

    serializer = serializers.BuyerSerializer(data=data)

    assert serializer.is_valid()
    instance = serializer.save()
    assert instance.email == data['email']
    assert instance.name == data['name']
    assert instance.sector == data['sector']
    assert instance.company_name == data['company_name']
    assert instance.country == data['country']
