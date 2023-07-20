import tablib
from django.core.management import BaseCommand
from import_export import fields, resources

from dataservices.models import Country


class CountryResource(resources.ModelResource):
    imported_rows_pk = []

    class Meta:
        model = Country
        skip_unchanged = True
        report_skipped = True
        is_active = fields.Field(default=True)
        import_id_fields = ['iso2']
        fields = ('name', 'iso1', 'iso2', 'iso3', 'region', 'is_active')

    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        self.Meta.model.objects.all().update(is_active=False)
        return super(CountryResource, self).before_import(dataset, using_transactions, dry_run, **kwargs)

    def get_or_init_instance(self, instance_loader, row):
        row['is_active'] = True
        return super(CountryResource, self).get_or_init_instance(instance_loader, row)


class Command(BaseCommand):
    help = 'Import Countries data'
    DEFAULT_FILENAME = 'dataservices/resources/countries-territories-and-regions-5.35.csv'

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument('filename', nargs='?', type=str)

    def handle(self, *args, **options):
        filename = options['filename'] if options['filename'] else self.DEFAULT_FILENAME
        with open(filename, 'r', encoding='utf-8-sig') as f:
            data = tablib.import_set(f.read(), format='csv', headers=True)
            dataset = tablib.Dataset(
                headers=[
                    'name',
                    'iso1',
                    'iso2',
                    'iso3',
                    'region',
                ]
            )

            # add only contries and selected columns
            for item in data:
                if item[2] == 'Country':
                    dataset.append((item[1], item[3], item[4], item[5], item[6]))
                elif item[1] == 'Hong Kong':
                    dataset.append((item[1], item[3], item[4], item[5], item[6]))
            country_resource = CountryResource()
            report = country_resource.import_data(dataset)
            [
                self.stdout.write(self.style.SUCCESS(f'Results:  {key} : {value}'))
                for key, value in report.totals.items()
            ]
