from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, subscriber, timestamp):
        return six.text_type(subscriber.pk) + six.text_type(timestamp)


anonymous_unsubscribe_token = TokenGenerator()
