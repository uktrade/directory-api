from django.core.management import BaseCommand

from company.tests import factories


class Command(BaseCommand):
    help = 'Create a companies and case studies to facilitate testing search.'

    def handle(self, *args, **options):
        for i in range(100):
            factories.CompanyFactory(
                is_published_investment_support_directory=True,
                is_published_find_a_supplier=True,
            )

        for i in range(10):
            gold_company = factories.CompanyFactory(
                name='Gold limited {}'.format(i),
                description='Providing the richness of gold.',
                summary='Golden',
                is_published_investment_support_directory=True,
                is_published_find_a_supplier=True,
                keywords='Rich, Gold, Bank, Shiny',
            )

            for j in range(5):
                factories.CompanyCaseStudyFactory(
                    company=gold_company, title='Thick case study {}'.format(j), description='Gold is delicious.'
                )

            lead_company = factories.CompanyFactory(
                name='Lead group {}'.format(i),
                description='Providing the density of lead.',
                summary='Radiation protection',
                is_published_investment_support_directory=True,
                is_published_find_a_supplier=True,
                keywords='Packs, Thick, Heavy, Metal',
            )
            for j in range(5):
                factories.CompanyCaseStudyFactory(
                    company=lead_company,
                    title='Thick case study {}'.format(j),
                    description='We determined lead sinks in water.',
                )
