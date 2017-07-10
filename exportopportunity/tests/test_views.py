from unittest.mock import patch, Mock

from rest_framework import status
import pytest

from django.core.urlresolvers import reverse

from exportopportunity import models


@pytest.mark.django_db
@patch('api.signature.SignatureCheckPermission.has_permission', Mock)
def test_export_opportunity_create(authed_client):
    assert models.ExportOpportunity.objects.count() == 0

    response = authed_client.post(reverse('export-opportunity-create'))

    assert response.status_code == status.HTTP_201_CREATED
    assert models.ExportOpportunity.objects.count() == 1
