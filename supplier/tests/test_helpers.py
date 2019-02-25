from supplier import helpers


def test_sso_user_pk():
    user = helpers.SSOUser(id=123, email='123@example.com')

    assert user.pk == 123
