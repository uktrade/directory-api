import json
import factory
import factory.fuzzy

from directory_validators.constants import choices

from company.models import Company, CompanyCaseStudy


def company_house_number():
    for i in range(10000000, 99999999):
        yield str(i)


EMPLOYEES_CHOICES = [choice[0] for choice in choices.EMPLOYEES]
EXPORT_STATUS_CHOICES = [choice[0] for choice in choices.EXPORT_STATUSES]


class FuzzySectorJson(factory.fuzzy.BaseFuzzyAttribute):
    def fuzz(self):
        sectors = [choice[0] for choice in choices.COMPANY_CLASSIFICATIONS]
        random_sector = factory.fuzzy._random.choice(sectors)
        return json.dumps([random_sector])


class CompanyFactory(factory.django.DjangoModelFactory):

    number = factory.Iterator(company_house_number())
    name = factory.fuzzy.FuzzyText(length=12)
    summary = factory.fuzzy.FuzzyText(length=50)
    description = factory.fuzzy.FuzzyText(length=50)
    employees = factory.fuzzy.FuzzyChoice(EMPLOYEES_CHOICES)
    export_status = factory.fuzzy.FuzzyChoice(EXPORT_STATUS_CHOICES)
    keywords = factory.fuzzy.FuzzyText(length=20)
    # TODO: Currently we can't use ImageField because of botocore issues
    # logo = factory.django.ImageField()
    sectors = FuzzySectorJson()
    website = factory.LazyAttribute(
        lambda company: 'http://%s.example.com' % company.name)
    date_of_creation = None
    twitter_url = factory.LazyAttribute(
        lambda company: 'http://twitter.com/%s' % company.name)
    facebook_url = factory.LazyAttribute(
        lambda company: 'http://facebook.com/%s' % company.name)
    linkedin_url = factory.LazyAttribute(
        lambda company: 'http://linkedin.com/%s' % company.name)
    mobile_number = factory.fuzzy.FuzzyText(length=11, chars='1234567890')
    postal_full_name = factory.fuzzy.FuzzyText(length=12)
    address_line_1 = factory.fuzzy.FuzzyText(length=12)
    address_line_2 = factory.fuzzy.FuzzyText(length=12)
    locality = factory.fuzzy.FuzzyText(length=12)
    country = factory.fuzzy.FuzzyChoice(
        ['Germany', 'China', 'Japan', 'Saudi Arabia', 'Nigeria'])
    postal_code = factory.Sequence(lambda n: "W{n}W {n}QB".format(n=n))
    po_box = factory.fuzzy.FuzzyText(length=3)
    email_full_name = factory.fuzzy.FuzzyText(length=12)
    email_address = factory.LazyAttribute(
        lambda company: '%s@example.com' % company.name)

    class Meta:
        model = Company


class CompanyCaseStudyFactory(factory.django.DjangoModelFactory):

    title = factory.fuzzy.FuzzyText(length=12)
    description = factory.fuzzy.FuzzyText(length=12)
    company = factory.SubFactory(CompanyFactory)

    class Meta:
        model = CompanyCaseStudy
