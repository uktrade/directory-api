from django.urls import reverse
from unittest import TestCase

from django.test import Client
from django.contrib.auth.models import User

class ExportOpportunityAdminTestCase(TestCase):

    def setUp(self):
        superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='test'
        )
        self.client = Client()
        self.client.force_login(superuser)

    def get_export_opportunities_food(self):
        response = self.client.get(
            reverse('admin:exportopportunity_exportopportnityfood')
        )
        assert response.status_code == 200

    def get_export_opportunities_legal(self):
        response = self.client.post(
            reverse('admin:exportopportunity_exportopportnitylegal')
        )

        assert response.status_code == 200
