from exportplan import models


def is_ep_plan_empty(plan, fields):
    if not plan.ui_progress:
        return True

    for section in fields:
        try:
            attr = getattr(plan, section).all()
            print("Try", attr)
            if attr:
                return False
        except:
            attr = getattr(plan, section)
            print("Except", attr)
            if attr:
                return False
    return True


def set_useable_fields():
    not_needed_model_fields = [
        "id",
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
