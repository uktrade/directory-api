from django.core.management import BaseCommand
from dataservices import helpers, models


class Command(BaseCommand):
    help = 'Preload seed data for dataservice comtrade cache'

    def handle(self, *args, **options):
        commodity_code = '2208.50.00.57'
        class_name = 'dataservices.helpers'
        countries = helpers.MADB().get_madb_country_list()
        function_names = ['get_last_year_import_data', 'get_last_year_import_data']
        models.DataServicesCacheLoad.objects.filter(class_name=class_name).delete()

        for country in countries:
            for function_name in function_names:
                function_dict = {'commodity_code': commodity_code, 'country': country[0]}
                data_item = models.DataServicesCacheLoad(
                    class_name=class_name,
                    function_name=function_name,
                    function_parameters=function_dict,
                )
                data_item.save()
        self.stdout.write(self.style.SUCCESS('All done, bye!'))
