from user.models import User as Supplier


def remove_supplier_company_ownership(sender, instance, *args, **kwargs):
    if instance.is_company_owner:
        Supplier.objects.filter(company=instance.company).update(
            is_company_owner=False
        )
