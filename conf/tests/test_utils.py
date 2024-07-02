from conf.utils import strip_password_data


def test_strip_password_data():
    event_with_password = strip_password_data({'request': {'data': {'password': 'abc123'}}}, None)
    strip_password_data({'request': {}}, None)  # Assure no error is raise when no password is present

    assert event_with_password['request']['data']['password'] is None
