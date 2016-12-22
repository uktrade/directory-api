import http
from unittest import TestCase

import pytest

from django.test import Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from company.models import Company
from company.tests import CompanyFactory


@pytest.mark.django_db
class PublishCompaniesInCSVTestCase(TestCase):
    # TODO: Test for bad data (whitespace, different format etc.)
    # TODO: GET view call to actually input data
    # TODO: Redirect after POST (try generic view instead of admin method)
    # TODO: Form validation for company nums that don't exist

    def setUp(self):
        superuser = User.objects.create_superuser(
            username='admin', email='admin@example.com', password='test'
        )
        self.client = Client()
        self.client.force_login(superuser)

    def test_uploaded_companies_set_to_published(self):
        companies = CompanyFactory.create_batch(5, is_published=False)
        published_company = CompanyFactory(is_published=True)
        numbers = '{num1},{num2}'.format(
            num1=companies[0].number, num2=companies[3].number)

        response = self.client.post(
            reverse('admin:company_company_publish'),
            {'company_numbers': numbers},
        )

        assert response.status_code == http.client.OK

        published = Company.objects.filter(is_published=True).values_list(
            'number', flat=True)
        assert len(published) == 3
        assert companies[0].number in published
        assert companies[3].number in published
        assert published_company.number in published

        unpublished = Company.objects.filter(is_published=False).values_list(
            'number', flat=True)
        assert len(unpublished) == 3
        assert companies[1].number in unpublished
        assert companies[2].number in unpublished
        assert companies[4].number in unpublished


@pytest.mark.django_db
class CompanyAdminAuthTestCase(TestCase):

    def setUp(self):
        self.client = Client()
        self.company = CompanyFactory()

    def test_nonsuperuser_cannot_access_company_publish_view(self):
        user = User.objects.create_user(
            username='admin', email='admin@example.com', password='test'
        )
        self.client.force_login(user)
        url = reverse('admin:company_company_publish')

        response = self.client.post(
            url, {'company_numbers': self.company.number})

        assert response.status_code == http.client.FOUND
        assert response.url == '/admin/login/?next={redirect_to}'.format(
            redirect_to=url)

    def test_guest_cannot_access_company_publish_view(self):
        url = reverse('admin:company_company_publish')

        response = self.client.post(
            url, {'company_numbers': self.company.number})

        assert response.status_code == http.client.FOUND
        assert response.url == '/admin/login/?next={redirect_to}'.format(
            redirect_to=url)
