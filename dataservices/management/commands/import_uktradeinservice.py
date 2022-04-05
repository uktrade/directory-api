import csv

from django.core.management import BaseCommand

from dataservices.models import Country, UKTradeInServiceByCountry


class Command(BaseCommand):
    help = 'Import population urban versus rural'

    import_years = [
        '2016',
        '2017',
        '2018',
        '2019',
        '2020',
        '2021',
        '2022',
    ]
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']

    def handle(self, *args, **options):
        data = []

        with open('dataservices/resources/servicetypebycountrydataset.csv', 'r', encoding='utf-8-sig') as f:
            file_reader = csv.DictReader(f)

            for row in file_reader:

                try:
                    country = Country.objects.get(iso2=row['Country code'].zfill(2))

                except Country.DoesNotExist:
                    country = None
                    self.stdout.write(f'No country match for {row["Country code"]}')
                    if not country:
                        continue
                for year in self.import_years:
                    value = row.get(year)
                    quarter = None
                    if value and value not in ['..']:
                        data.append(
                            UKTradeInServiceByCountry(
                                direction=row['Direction'].upper(),
                                servicetype_code=row['Service type code'],
                                service_type=row['Service type'],
                                country=country,
                                quarter=quarter,
                                year=year,
                                value=value,
                            )
                        )
                    for quarter in range(1, 5):
                        value = row.get(year + 'Q' + str(quarter))
                        if value and value not in ['..']:
                            data.append(
                                UKTradeInServiceByCountry(
                                    direction=row['Direction'].upper(),
                                    servicetype_code=row['Service type code'],
                                    service_type=row['Service type'],
                                    country=country,
                                    quarter=quarter,
                                    year=year,
                                    value=value,
                                )
                            )

            UKTradeInServiceByCountry.objects.all().delete()
            UKTradeInServiceByCountry.objects.bulk_create(data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
