import factory
import factory.fuzzy
from directory_constants import choices, user_roles
from django.utils.text import slugify
from faker import Faker

from company import models


def company_house_number():
    for i in range(10000000, 99999999):
        yield str(i)


EMPLOYEES_CHOICES = [choice[0] for choice in choices.EMPLOYEES]

fake = Faker()
fake.add_provider(factory.Faker('building_number'))
fake.add_provider(factory.Faker('street_name'))


class CompanyFactory(factory.django.DjangoModelFactory):

    number = factory.Iterator(company_house_number())
    name = factory.Faker('company')
    summary = factory.Faker('catch_phrase')
    description = factory.fuzzy.FuzzyText(length=50)
    employees = factory.fuzzy.FuzzyChoice([i[0] for i in EMPLOYEES_CHOICES])
    has_exported_before = False
    keywords = factory.fuzzy.FuzzyText(length=20)
    # TODO: Currently we can't use ImageField because of botocore issues
    # logo = factory.django.ImageField()
    sectors = factory.fuzzy.FuzzyChoice([i[0] for i in choices.INDUSTRIES])
    hs_codes = ['1', '2']
    expertise_industries = factory.fuzzy.FuzzyChoice([i[0] for i in choices.INDUSTRIES])
    expertise_regions = factory.fuzzy.FuzzyChoice([i[0] for i in choices.EXPERTISE_REGION_CHOICES])
    expertise_languages = factory.fuzzy.FuzzyChoice([i[0] for i in choices.EXPERTISE_LANGUAGES])
    expertise_countries = factory.fuzzy.FuzzyChoice([i[0] for i in choices.COUNTRY_CHOICES])
    expertise_products_services = {
        "other": ['Regulatory', 'Finance', 'IT'],
        "Finance": ['Insurance'],
    }
    website = factory.LazyAttribute(lambda company: f'http://{company.name}.example.com')
    date_of_creation = None
    twitter_url = factory.LazyAttribute(lambda company: f'http://twitter.com/{company.name}')
    facebook_url = factory.LazyAttribute(lambda company: f'http://facebook.com/{company.name}')
    linkedin_url = factory.LazyAttribute(lambda company: f'http://linkedin.com/{company.name}')
    mobile_number = factory.fuzzy.FuzzyText(length=11, chars='1234567890')

    @factory.lazy_attribute
    def address_line_1(self):
        return '{0} {1}'.format(fake.building_number(), fake.street_name())

    address_line_2 = factory.Faker('city', locale='en_GB')
    locality = factory.fuzzy.FuzzyText(length=12)
    country = factory.fuzzy.FuzzyChoice(['Germany', 'China', 'Japan', 'Saudi Arabia', 'Nigeria'])
    postal_code = factory.Faker('postcode', locale='en_GB')
    po_box = factory.fuzzy.FuzzyText(length=3)
    email_full_name = factory.Faker('name')
    postal_full_name = email_full_name
    email_address = factory.LazyAttribute(lambda x: f'{slugify(x.name)}@example.com')

    class Meta:
        model = models.Company


class CompanyCaseStudyFactory(factory.django.DjangoModelFactory):

    title = factory.fuzzy.FuzzyText(length=12)
    description = factory.fuzzy.FuzzyText(length=12)
    company = factory.SubFactory(CompanyFactory)

    class Meta:
        model = models.CompanyCaseStudy


class CollaborationInviteFactory(factory.django.DjangoModelFactory):

    collaborator_email = factory.Sequence(lambda n: f'{n}@example.com')
    company = factory.SubFactory(CompanyFactory)
    company_user = factory.SubFactory('company.tests.factories.CompanyUserFactory')
    accepted = False
    accepted_date = None
    role = user_roles.EDITOR

    class Meta:
        model = models.CollaborationInvite


class CollaborationRequestFactory(factory.django.DjangoModelFactory):

    requestor = factory.SubFactory('company.tests.factories.CompanyUserFactory')
    accepted = False
    accepted_date = None
    role = user_roles.ADMIN
    name = factory.Faker('name', locale='en_GB')

    class Meta:
        model = models.CollaborationRequest


class CompanyUserFactory(factory.django.DjangoModelFactory):
    sso_id = factory.fuzzy.FuzzyInteger(1, 9999)
    name = factory.Faker('name', locale='en_GB')
    mobile_number = factory.fuzzy.FuzzyText(length=11, chars='1234567890')
    company_email = factory.LazyAttribute(lambda x: f'{slugify(x.name)}-{x.sso_id}@example.com')
    company = factory.SubFactory(CompanyFactory)
    role = user_roles.ADMIN

    class Meta:
        model = models.CompanyUser
