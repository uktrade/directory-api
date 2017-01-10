import factory
import factory.fuzzy

from company.models import Company, CompanyCaseStudy


def company_house_number():
    for i in range(10000000, 99999999):
        yield str(i)


class CompanyFactory(factory.django.DjangoModelFactory):

    number = factory.Iterator(company_house_number())
    name = factory.fuzzy.FuzzyText(length=12)

    class Meta:
        model = Company


class CompanyCaseStudyFactory(factory.django.DjangoModelFactory):

    title = factory.fuzzy.FuzzyText(length=12)
    description = factory.fuzzy.FuzzyText(length=12)
    company = factory.SubFactory(CompanyFactory)

    class Meta:
        model = CompanyCaseStudy
