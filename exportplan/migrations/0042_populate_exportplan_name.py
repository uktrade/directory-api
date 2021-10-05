from django.db import migrations
from exportplan.helpers import get_unique_exportplan_name
from django.forms.models import model_to_dict


def populate_exportplan_name(apps, schema_editor):
    """
    Update `exportplan name` :
    """

    CompanyExportPlan = apps.get_model('exportplan', 'CompanyExportPlan')
    for export_plan in CompanyExportPlan.objects.filter(name__isnull=True):
        data = model_to_dict(export_plan)
        export_plan.name = get_unique_exportplan_name(data)
        export_plan.save()


class Migration(migrations.Migration):

    dependencies = [
        ('exportplan', '0041_derive_export_end_date'),
    ]

    operations = [
        migrations.RunPython(populate_exportplan_name, migrations.RunPython.noop),
    ]
