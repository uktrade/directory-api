from unittest import mock

from django.test import TestCase, RequestFactory

from signature.permissions import SignaturePermission


class BaseSignatureTestCase(TestCase):
    """
    Base TestCase providing a mock request and appropriate signature
    """

    def setUp(self):
        self.request = RequestFactory().get('/path')


class SignaturePermissionTestCase(BaseSignatureTestCase):

    def setUp(self):
        super().setUp()
        self.view = mock.Mock()
        self.request.user = mock.Mock()
        self.request.user.is_authenticated = lambda: False
        self.signature_permision = SignaturePermission().has_permission

    def test_has_permission_nonschema_invalid_signature(self):
        self.assertFalse(self.signature_permision(self.request, self.view))

    def test_has_permission_nonschema_not_authenticated(self):
        self.assertFalse(self.signature_permision(self.request, self.view))
