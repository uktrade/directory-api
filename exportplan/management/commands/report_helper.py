from exportplan import models
import csv


def is_ep_plan_empty(plan, fields):
    if not plan.ui_progress:
        return True

    for section in fields:
        try:
            attr = getattr(plan, section).all()
            if attr:
                return False
        except AttributeError:
            attr = getattr(plan, section)
            if attr:
                return False
    return True


def set_useable_fields():
    not_needed_model_fields = [
        "id",
        "name",
        "created",
        "modified",
        "sso_id",
        "company",
        "export_countries",
        "export_commodity_codes",
        "ui_progress",
    ]
    my_model_fields = [field.name for field in models.CompanyExportPlan._meta.get_fields()]
    return [field for field in my_model_fields if field not in not_needed_model_fields]


def write_ep_csv(ep_list):
    with open('ep_plan.csv', mode='w') as exportplan:
        fieldnames = ['sso_id', 'export_countries', 'export_commodity_codes']
        writer = csv.DictWriter(exportplan, fieldnames=fieldnames)

        writer.writeheader()
        for ep in ep_list:
            writer.writerow(
                {
                    'sso_id': ep["sso_id"],
                    'export_countries': ep["export_countries"],
                    'export_commodity_codes': ep["export_commodity_codes"],
                }
            )
