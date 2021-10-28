from django.apps import AppConfig
from django.db.models.signals import pre_save


class ExportplanConfig(AppConfig):
    name = 'exportplan'

    def ready(self):
        from exportplan import signals

        pre_save.connect(receiver=signals.update_exportplan_label_on_update, sender='exportplan.CompanyExportPlan')
