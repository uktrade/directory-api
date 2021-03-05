import csv

from django.core.management import BaseCommand

from dataservices.models import Country, PopulationData


class Command(BaseCommand):
    help = 'Import target age groups (male/female).'

    def handle(self, *args, **options):
        genders = ['male', 'female']
        population_data = []

        for gender in genders:
            with open(f'dataservices/resources/world_population_medium_{gender}.csv', 'r', encoding='utf-8-sig') as f:
                file_reader = csv.DictReader(f)

                for row in file_reader:
                    try:
                        country = Country.objects.get(iso1=row['country_code'])
                    except Country.DoesNotExist:
                        country = None

                    population_data.append(
                        PopulationData(
                            country=country,
                            year=row['year'] if row['year'] else None,
                            gender=gender,
                            age_0_4=row['0-4'] if row['0-4'] and row['0-4'] != '...' else None,
                            age_5_9=row['5-9'] if row['5-9'] and row['5-9'] != '...' else None,
                            age_10_14=row['10-14'] if row['10-14'] and row['10-14'] != '...' else None,
                            age_15_19=row['15-19'] if row['15-19'] and row['15-19'] != '...' else None,
                            age_20_24=row['20-24'] if row['20-24'] and row['20-24'] != '...' else None,
                            age_25_29=row['25-29'] if row['25-29'] and row['25-29'] != '...' else None,
                            age_30_34=row['30-34'] if row['30-34'] and row['30-34'] != '...' else None,
                            age_35_39=row['35-39'] if row['35-39'] and row['35-39'] != '...' else None,
                            age_40_44=row['40-44'] if row['40-44'] and row['40-44'] != '...' else None,
                            age_45_49=row['45-49'] if row['45-49'] and row['45-49'] != '...' else None,
                            age_50_54=row['50-54'] if row['50-54'] and row['50-54'] != '...' else None,
                            age_55_59=row['55-59'] if row['55-59'] and row['55-59'] != '...' else None,
                            age_60_64=row['60-64'] if row['60-64'] and row['60-64'] != '...' else None,
                            age_65_69=row['65-69'] if row['65-69'] and row['65-69'] != '...' else None,
                            age_70_74=row['70-74'] if row['70-74'] and row['70-74'] != '...' else None,
                            age_75_79=row['75-79'] if row['75-79'] and row['75-79'] != '...' else None,
                            age_80_84=row['80-84'] if row['80-84'] and row['80-84'] != '...' else None,
                            age_85_89=row['85-89'] if row['85-89'] and row['85-89'] != '...' else None,
                            age_90_94=row['90-94'] if row['90-94'] and row['90-94'] != '...' else None,
                            age_95_99=row['95-99'] if row['95-99'] and row['95-99'] != '...' else None,
                            age_100_plus=row['100+'] if row['100+'] and row['100+'] != '...' else None,
                        )
                    )

            PopulationData.objects.all().delete()
            PopulationData.objects.bulk_create(population_data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
