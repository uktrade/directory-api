from supplier import helpers


def test_sso_user_pk():
    user = helpers.SSOUser(id=123, email='123@example.com')

    assert user.pk == 123


def test_sso_full_name():
    user_profile = {'first_name': 'big', 'last_name': 'name'}
    user = helpers.SSOUser(id=123, email='123@example.com', user_profile=user_profile)
    user_no_profile = helpers.SSOUser(id=123, email='123@example.com')

    user_profile_first_name = {'first_name': 'big'}
    user_profile_last_name = {'last_name': 'name'}

    user_first_name = helpers.SSOUser(id=123, email='123@example.com', user_profile=user_profile_first_name)
    user_last_name = helpers.SSOUser(id=123, email='123@example.com', user_profile=user_profile_last_name)

    assert user.full_name == 'big name'
    assert user_no_profile.full_name == ''
    assert user_first_name.full_name == 'big'
    assert user_last_name.full_name == ''
