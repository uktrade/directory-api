import tablib
from django.core.management import BaseCommand

from dataservices.models import Country, RuleOfLaw


class Command(BaseCommand):
    help = 'Import Income data'

    def handle(self, *args, **options):
        with open('dataservices/resources/rule_of_law_rank.csv', 'r', encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            ruleoflaw_data = []

            for item in data:
                try:
                    country = Country.objects.get(iso2=item[4])
                except Country.DoesNotExist:
                    country = None

                score = item[2] if item[2] else None
                ruleoflaw_data.append(
                    RuleOfLaw(country_name=item[0], iso2=item[4], country=country, score=score, rank=item[1])
                )
            RuleOfLaw.objects.all().delete()
            RuleOfLaw.objects.bulk_create(ruleoflaw_data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
