from django.apps import AppConfig
from django.db.models.signals import post_save

from exportopportunity import signals


class ExportOpportunityConfig(AppConfig):
    name = 'exportopportunity'

    def ready(self):
        post_save.connect(
            receiver=signals.send_opportunity_to_post,
            sender='exportopportunity.ExportOpportunityFood'
        )
        post_save.connect(
            receiver=signals.send_opportunity_to_post,
            sender='exportopportunity.ExportOpportunityLegal'
        )
