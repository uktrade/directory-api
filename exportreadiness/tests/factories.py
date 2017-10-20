import uuid

import factory

from directory_constants.constants import comtrade_choices

from exportreadiness import models


class TriageResultFactory(factory.django.DjangoModelFactory):

    sector = comtrade_choices.SECTORS_CHOICES[0][0]  # HS01 Animals live
    exported_before = True
    regular_exporter = True
    used_online_marketplace = False
    company_name = factory.fuzzy.FuzzyText(length=12)
    sole_trader = False

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
