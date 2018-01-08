from company.tests import factories


def build_company_factory(Company):
    """Factory function that returns a CompanyFactory

    This allows creating a CompanyFactory that works in migration tests. The
    factory `company.tests.factories.CompanyFactory` uses
    `company.models.Company`, so it cannot be used in migration tests for the
    same reason that during migrations we have to use `apps.get_model(...)`

    """

    class HistoricCompanyFactory(factories.CompanyFactory):
        class Meta:
            model = Company
    return HistoricCompanyFactory


def build_collaborator_invite_factory(CollaboratorInvite):
    class HistoricCollaboratorFactory(factories.CollaboratorInviteFactory):
        class Meta:
            model = CollaboratorInvite
    return HistoricCollaboratorFactory


def build_ownership_invite_factory(OwnershipInvite):
    class HistoricOwnershipInviteFactory(factories.OwnershipInviteFactory):
        class Meta:
            model = OwnershipInvite
    return HistoricOwnershipInviteFactory
