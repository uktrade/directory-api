from exportreadiness.tests import factories


def build_triage_result_factory(TriageResultFactory):
    class HistoricTriageResultFactory(factories.TriageResultFactory):
        class Meta:
            model = TriageResultFactory

    return HistoricTriageResultFactory
