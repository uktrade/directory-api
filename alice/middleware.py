import logging

from django.http import HttpResponseBadRequest

from alice.utils import SignatureRejection


class SignatureRejectionMiddleware(object):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def process_request(self, request):
        if not SignatureRejection.test_signature(request):
            return HttpResponseBadRequest("PFO")
        return None
