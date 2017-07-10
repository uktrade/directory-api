import factory

from exportopportunity import models


class ExportOpportunityFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.ExportOpportunity
