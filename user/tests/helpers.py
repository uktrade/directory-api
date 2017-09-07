from supplier.tests import factories


def build_user_factory(HistoricUser):
    class HistoricUserFactory(factories.SupplierFactory):
        class Meta:
            model = HistoricUser
        company = None

    return HistoricUserFactory
