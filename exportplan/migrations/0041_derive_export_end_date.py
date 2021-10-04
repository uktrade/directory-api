import django.core.validators
from django.db import migrations, models
from dateutil.relativedelta import relativedelta


def derive_export_end_date(apps, schema_editor):
    """
    Update `total_costs_and_price` JSON:
    - If `units_to_export_second_period` key exists, add `export_end` key based on export
      plan modified date and given unit/value
    - If `units_to_export_first_period` key exists, add new `export_quantity` key

    Leaving existing values in place for reference.
    """
    CompanyExportPlan = apps.get_model('exportplan', 'CompanyExportPlan')
    for export_plan in CompanyExportPlan.objects.all():
        if export_plan.total_cost_and_price.get('units_to_export_second_period'):
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
                        'year': new_end_date.year
                    }
                    export_plan.save()

        if export_plan.total_cost_and_price.get('units_to_export_first_period'):
            export_plan.total_cost_and_price['export_quantity'] = export_plan.total_cost_and_price['units_to_export_first_period']
            export_plan.save()


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0039_auto_20210726_1520'),
    ]

    operations = [
        migrations.RunPython(derive_export_end_date),
    ]
