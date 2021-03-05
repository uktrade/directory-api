import tablib
from django.core.management import BaseCommand

from dataservices.models import Country, PopulationData


class Command(BaseCommand):
    help = 'Import target age groups (male/female).'

    def handle(self, *args, **options):
        genders = ['male', 'female']
        population_data = []

        for gender in genders:
            with open(f'dataservices/resources/world_population_medium_{gender}.csv', 'r', encoding='utf-8-sig') as f:
                data = tablib.import_set(f.read(), format='csv', headers=True)

                for item in data:
                    try:
                        country = Country.objects.get(iso1=item[1])
                    except Country.DoesNotExist:
                        country = None

                    population_data.append(
                        PopulationData(
                            country=country,
                            year=item[3] if item[3] else None,
                            gender=gender,
                            age_0_4=item[4] if item[4] and item[4] != '...' else None,
                            age_5_9=item[5] if item[5] and item[5] != '...' else None,
                            age_10_14=item[6] if item[6] and item[6] != '...' else None,
                            age_15_19=item[7] if item[7] and item[7] != '...' else None,
                            age_20_24=item[8] if item[8] and item[8] != '...' else None,
                            age_25_29=item[9] if item[9] and item[9] != '...' else None,
                            age_30_34=item[10] if item[10] and item[10] != '...' else None,
                            age_35_39=item[11] if item[11] and item[11] != '...' else None,
                            age_40_44=item[12] if item[12] and item[12] != '...' else None,
                            age_45_49=item[13] if item[13] and item[13] != '...' else None,
                            age_50_54=item[14] if item[14] and item[14] != '...' else None,
                            age_55_59=item[15] if item[15] and item[15] != '...' else None,
                            age_60_64=item[16] if item[16] and item[16] != '...' else None,
                            age_65_69=item[17] if item[17] and item[17] != '...' else None,
                            age_70_74=item[18] if item[18] and item[18] != '...' else None,
                            age_75_79=item[19] if item[19] and item[19] != '...' else None,
                            age_80_84=item[20] if item[20] and item[20] != '...' else None,
                            age_85_89=item[21] if item[21] and item[21] != '...' else None,
                            age_90_94=item[22] if item[22] and item[22] != '...' else None,
                            age_95_99=item[23] if item[23] and item[23] != '...' else None,
                            age_100_plus=item[24] if item[24] and item[24] != '...' else None,
                        )
                    )

            PopulationData.objects.all().delete()
            PopulationData.objects.bulk_create(population_data)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
