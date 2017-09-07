def remove_supplier_company_ownership(sender, instance, *args, **kwargs):
    if instance.company and instance.is_company_owner:
        instance.company.suppliers.exclude(
            pk=instance.pk
        ).update(
            is_company_owner=False
        )
