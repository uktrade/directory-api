import factory

from exportreadiness.models import TriageResult


class TriageResultFactory(factory.django.DjangoModelFactory):

    sector = 'Foo'
    exported_before = True
    regular_exporter = True
    used_online_marketplace = False
    company_name = factory.fuzzy.FuzzyText(length=12)
    sole_trader = False

    class Meta:
        model = TriageResult
