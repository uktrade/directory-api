def is_ep_plan_empty(plan, fields):
    print(fields)
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
