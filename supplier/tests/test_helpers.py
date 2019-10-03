from supplier import helpers


def test_sso_user_pk():
    user = helpers.SSOUser(id=123, email='123@example.com')

    assert user.pk == 123


def test_sso_full_name():
    user = helpers.SSOUser(id=123, email='123@example.com', first_name='big', last_name='name')
    user_no_name = helpers.SSOUser(id=123, email='123@example.com')
    user_first_name = helpers.SSOUser(id=123, email='123@example.com', first_name='big')
    user_last_name = helpers.SSOUser(id=123, email='123@example.com', last_name='name')
    assert user.full_name == 'big name'
    assert user_no_name.full_name == ''
    assert user_first_name.full_name == 'big'
    assert user_last_name.full_name == ''
