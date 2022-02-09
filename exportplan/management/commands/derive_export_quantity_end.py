from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand

from exportplan import models


class Command(BaseCommand):
    def handle(self, *args, **options):
        count = 0
        for export_plan in models.CompanyExportPlan.objects.all():
            updated = False

            if export_plan.total_cost_and_price.get(
                'units_to_export_second_period'
            ) and not export_plan.total_cost_and_price.get('export_end'):
                unit = export_plan.total_cost_and_price['units_to_export_second_period'].get('unit')
                value = export_plan.total_cost_and_price['units_to_export_second_period'].get('value')

                if unit and value:
                    if unit == 'd':
                        delta = relativedelta(days=+value)
                    elif unit == 'm':
                        delta = relativedelta(months=+value)
                    elif unit == 'y':
                        delta = relativedelta(years=+value)
                    else:
                        delta = False

                    if delta:
                        new_end_date = export_plan.modified + delta
                        export_plan.total_cost_and_price['export_end'] = {
                            'month': new_end_date.month,
                            'year': new_end_date.year,
                        }
                        export_plan.save()
                        updated = True

            if export_plan.total_cost_and_price.get(
                'units_to_export_first_period'
            ) and not export_plan.total_cost_and_price.get('export_quantity'):
                export_plan.total_cost_and_price['export_quantity'] = export_plan.total_cost_and_price[
                    'units_to_export_first_period'
                ]
                export_plan.save()
                updated = True

            if updated is True:
                count += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {count} export plans"))
