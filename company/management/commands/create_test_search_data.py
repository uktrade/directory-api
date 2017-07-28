from django.core.management import BaseCommand

from company.tests import factories


class Command(BaseCommand):

    help = 'Create a companies and case studies to facilitate testing search.'

    def handle(self, *args, **options):
        for i in range(30):
            factories.CompanyFactory(
                name='Aardvark limited {}'.format(i),
                description='Providing the power and beauty of Aardvarks.',
                summary='Like an Aardvark',
                is_published=True,
                keywords='Ants, Tongue, Anteater',
            )
            factories.CompanyFactory(
                name='Wolf limited {}'.format(i),
                description='Providing the stealth and prowess of wolves.',
                summary='Hunts in packs',
                is_published=True,
                keywords='Packs, Hunting, Stark, Teeth',
            )
            factories.CompanyFactory(
                name='Grapeshot limited {}'.format(i),
                description='Providing the destructiveness of grapeshot.',
                summary='Like naval warfare',
                is_published=True,
                keywords='Pirates, Ocean, Ship',
            )

        for i in range(10):
            gold_company = factories.CompanyFactory(
                name='Gold limited {}'.format(i),
                description='Providing the richness of gold.',
                summary='Golden',
                is_published=True,
                keywords='Rich, Gold, Bank, Shiny',
            )

            for j in range(5):
                factories.CompanyCaseStudyFactory(
                    company=gold_company,
                    title='Thick case study {}'.format(j),
                    description='Gold is delicious.'
                )

            lead_company = factories.CompanyFactory(
                name='Lead group {}'.format(i),
                description='Providing the density of lead.',
                summary='Radiation protection',
                is_published=True,
                keywords='Packs, Thick, Heavy, Metal',
            )
            for j in range(5):
                factories.CompanyCaseStudyFactory(
                    company=lead_company,
                    title='Thick case study {}'.format(j),
                    description='We determined lead sinks in water.'
                )
