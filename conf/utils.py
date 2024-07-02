def strip_password_data(event, hint):
    """
    Looks in the data of a Sentry request and removes the password key, if it exists.
    """

    try:
        event['request']['data']['password'] = None
    except KeyError:
        pass

    return event
