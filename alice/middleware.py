import logging

from hashlib import sha256

from django.conf import settings
from django.http import HttpResponseBadRequest
from django.utils.crypto import constant_time_compare


class SignatureRejectionMiddleware(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_request(self, request):
        if not self._test_signature(request):
            return HttpResponseBadRequest("PFO")
        return None

    def _generate_signature(self, secret, path, body):
        salt = bytes(secret, "utf-8")
        path = bytes(path, "utf-8")
        return sha256(path + body + salt).hexdigest()

    def _test_signature(self, request):
        offered = request.META.get("HTTP_X_SIGNATURE")

        if not offered:
            return False

        generated = self._generate_signature(
            settings.UI_SECRET,
            request.get_full_path(),
            request.body,
        )
        return constant_time_compare(generated, offered)
