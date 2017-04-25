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


def test_new_companies_in_sector_limit_companies():
    notification = email.NewCompaniesInSectorNotification(
        subscriber={'email': 'jim@examle.com', 'name': 'Jim'},
        companies=[1, 2, 3, 4, 5, 6, 7, 8, 9],
    )
    context = notification.get_context_data()
    assert len(context['companies']) == 5
