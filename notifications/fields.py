from django.core.signing import BadSignature, Signer
from rest_framework import exceptions, fields


class SignedEmailField(fields.EmailField):
    def to_internal_value(self, data):
        try:
            unsigned = Signer().unsign(data)
        except BadSignature:
            raise exceptions.ValidationError('Bad signature')
        else:
            return super().to_internal_value(unsigned)
