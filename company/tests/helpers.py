from company.tests.factories import CompanyFactory


def company_factory_factory(Company):
    """Factory function that returns a CompanyFactory

    This allows creating a CompanyFactory that works in migration tests. The
    factory `company.tests.factories.CompanyFactory` uses
    `company.models.Company`, so it cannot be used in migration tests for the
    same reason that during migrations we have to use `apps.get_model(...)`

    """

    class HistoricCompanyFactory(CompanyFactory):
        class Meta:
            model = Company
    return HistoricCompanyFactory
