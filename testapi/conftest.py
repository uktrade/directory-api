import pytest

from user import models


@pytest.fixture
def active_user():
    return models.User.objects.create_user(
        email="test@user.com",
        password="password",
        is_active=True,
        sso_id=1
    )


@pytest.fixture
def inactive_user():
    return models.User.objects.create_user(
        email="inactive@user.com",
        password="password",
        is_active=False,
        sso_id=2
    )
