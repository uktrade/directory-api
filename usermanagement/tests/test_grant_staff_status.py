import pytest
from django.contrib.auth.models import User
from django.core.management import call_command


@pytest.mark.django_db
def test_grant_staff_status():
    username = 'testuser@.com'
    user = User.objects.create_user(username=username)
    user.save()

    assert user.is_staff is False
    call_command('grant_staff_status', username)
    user.refresh_from_db()
    assert user.is_staff is True


@pytest.mark.django_db
def test_grant_staff_status_user_no_found():

    username = 'testuser@testuser.com'
    call_command('grant_staff_status', username)
