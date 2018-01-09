from supplier.tests import factories


def build_supplier_factory(Supplier):
    class HistoricSupplierFactory(factories.SupplierFactory):
        class Meta:
            model = Supplier
    return HistoricSupplierFactory
