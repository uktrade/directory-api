import factory
import factory.fuzzy

from enrolment import models


class PreVerifiedCompanyFactory(factory.django.DjangoModelFactory):

    company_number = factory.fuzzy.FuzzyText(length=8)
    email_address = factory.Sequence(lambda n: '%d@example.com' % n)
    is_active = True

    class Meta:
        model = models.PreVerifiedCompany
