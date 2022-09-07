from django.contrib.auth.tokens import PasswordResetTokenGenerator


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, subscriber, timestamp):
        return str(subscriber.pk) + str(timestamp)


anonymous_unsubscribe_token = TokenGenerator()
