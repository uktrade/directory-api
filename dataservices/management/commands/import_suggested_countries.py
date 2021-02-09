import tablib
from django.core.management import BaseCommand

from core.helpers import get_s3_file_stream
from dataservices.models import Country, SuggestedCountry


class Command(BaseCommand):
    help = 'Import Countries data from S3'

    def handle(self, *args, **options):
        filestream = get_s3_file_stream('SR.CREST.ALL.csv')
        data = tablib.import_set(filestream, format='csv', headers=True)
        suggested_product_countries = []

        # add only countries and selected columns
        for suggested_tuple in data:
            # for suggested_tuple in data:
            iso_list = []
            hs_code = None
            for item in suggested_tuple:
                if item.isnumeric():
                    hs_code = item
                elif len(item) == 2:
                    iso_list.append(item)

            suggested_countries = Country.objects.filter(iso2__in=iso_list)

            if hs_code and len(suggested_countries) > 0:
                order = 1
                for country in suggested_countries:
                    suggested_product_countries.append(SuggestedCountry(hs_code=hs_code, country=country, order=order))
                    order += 1

        SuggestedCountry.objects.all().delete()
        SuggestedCountry.objects.bulk_create(suggested_product_countries)

        self.stdout.write(self.style.SUCCESS('All done, bye!'))
