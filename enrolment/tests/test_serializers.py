import json
from unittest.mock import Mock, patch

from rest_framework.serializers import ValidationError
import pytest

from enrolment.serializers import EnrolmentSerializer
from enrolment.tests import VALID_REQUEST_DATA
from enrolment.models import Enrolment
from company.models import Company
from user.models import User


@pytest.mark.django_db
def test_create_company_exception_rollback():
    for i, exception_class in enumerate([Exception, ValidationError]):
        stub = Mock(side_effect=exception_class('!'))

        invalid_data = VALID_REQUEST_DATA.copy()
        invalid_data['company_number'] = None

        with patch.object(EnrolmentSerializer, 'create_company', stub):
            with pytest.raises(exception_class):
                serializer = EnrolmentSerializer(data={
                    'data': json.dumps(invalid_data)
                })
                assert serializer.is_valid()
                serializer.save()
            # we want the enrolment to save
            assert Enrolment.objects.count() == i + 1
            # but we want the Company to not exist without User
            assert Company.objects.count() == 0
            assert User.objects.count() == 0


@pytest.mark.django_db
def test_create_user_exception_rollback():
    for i, exception_class in enumerate([Exception, ValidationError]):
        stub = Mock(side_effect=exception_class('!'))

        invalid_data = VALID_REQUEST_DATA.copy()
        invalid_data['corporate_email'] = None

        with patch.object(EnrolmentSerializer, 'create_company', stub):
            with pytest.raises(exception_class):
                serializer = EnrolmentSerializer(data={
                    'data': json.dumps(invalid_data)
                })
                assert serializer.is_valid()
                serializer.save()
            # we want the enrolment to save
            assert Enrolment.objects.count() == i + 1
            # but we want the Company to not exist without User
            assert Company.objects.count() == 0
            assert User.objects.count() == 0
