from django.forms.models import model_to_dict

from exportplan.helpers import get_unique_exportplan_name


def update_exportplan_label_on_update(sender, instance, *args, **kwargs):
    # Not needed since name is added during serialiser here
    if instance._state.adding:
        return
    if len(instance.export_countries) and len(instance.export_commodity_codes):
        # Since this is only needed if either export_countries or export_commodity_codes was not selected
        previous_instance = sender.objects.get(id=instance.id)
        if not len(previous_instance.export_countries) or not len(previous_instance.export_commodity_codes):
            data = model_to_dict(instance)
            instance.name = get_unique_exportplan_name(data)
