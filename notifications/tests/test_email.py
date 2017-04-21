import pytest

from notifications import email


class NotificationMissingProperties(email.NotificationBase):
    pass


def test_notification_base_rejects_if_required_properties_missing():
    with pytest.raises(TypeError) as exc_info:
        NotificationMissingProperties()
    assert exc_info.exconly() == (
        "TypeError: Can't instantiate abstract class "
        "NotificationMissingProperties with abstract methods category, "
        "from_email, html_template, recipient, record_sent, subject, "
        "text_template, unsubscribe_url"
    )
