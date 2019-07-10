import factory
import factory.fuzzy
from faker import Faker

from redirects.models import Redirect

fake = Faker()


class RedirectFactory(factory.django.DjangoModelFactory):
    source_url = fake.url()
    target_url = fake.url()

    class Meta:
        model = Redirect
