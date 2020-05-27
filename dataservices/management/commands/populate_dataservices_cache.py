from django.core.management import BaseCommand
from dataservices import models
from importlib import import_module


class Command(BaseCommand):
    help = 'Preload dataservice cache'

    def handle(self, *args, **options):
        class_name = 'dataservices.helpers'
        dataservices_load_items = models.DataServicesCacheLoad.objects.filter(class_name=class_name)
        for dataservices_load_item in dataservices_load_items:
            dataservices_description = f'class_name {dataservices_load_item.class_name}: ' \
                                       f'function_name {dataservices_load_item.function_name}: ' \
                                       f'function_parameters {dataservices_load_item.function_name}'
            try:
                imported_module = import_module(dataservices_load_item.class_name)
                imported_function = getattr(imported_module, dataservices_load_item.function_name)
                imported_function(**dataservices_load_item.function_parameters)
                self.stdout.write(self.style.SUCCESS(f'{dataservices_description} updated'))
            except Exception as exception:
                self.stdout.write(self.style.SUCCESS(f'{dataservices_description} error'))
                self.stdout.write(self.style.ERROR(exception))
