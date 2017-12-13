import uuid

import factory

from directory_constants.constants import exred_sector_names

from exportreadiness import models


class TriageResultFactory(factory.django.DjangoModelFactory):

    sector = exred_sector_names.SECTORS_CHOICES[0][0]  # HS01 Animals live
    exported_before = True
    regular_exporter = True
    used_online_marketplace = False
    company_name = factory.fuzzy.FuzzyText(length=12)
    is_in_companies_house = True

    class Meta:
        model = models.TriageResult


class ArticleReadFactory(factory.django.DjangoModelFactory):

    article_uuid = factory.LazyFunction(uuid.uuid4)

    class Meta:
        model = models.ArticleRead


class TaskCompletedFactory(factory.django.DjangoModelFactory):

    task_uuid = factory.LazyFunction(uuid.uuid4)

    class Meta:
        model = models.TaskCompleted
