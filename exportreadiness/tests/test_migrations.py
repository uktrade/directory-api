import pytest
from exportreadiness.tests import helpers


@pytest.mark.django_db
def test_is_in_companies_house(migration):
    app_name = 'exportreadiness'
    model_name = 'TriageResult'
    historic_apps = migration.before([
        (app_name, '0009_auto_20171103_1157')
    ])

    HistoricTriageResult = historic_apps.get_model(app_name, model_name)
    HistoricTriageResultFactory = helpers.build_triage_result_factory(
        HistoricTriageResult
    )

    historic_result_one = HistoricTriageResultFactory.create(
        sole_trader=True, sso_id=1
    )
    historic_result_two = HistoricTriageResultFactory.create(
        sole_trader=False, sso_id=2,
    )

    apps = migration.apply(app_name, '0010_auto_20171103_1157')
    TriageResult = apps.get_model(app_name, model_name)

    assert TriageResult.objects.get(
        pk=historic_result_one.pk
    ).is_in_companies_house is False
    assert TriageResult.objects.get(
        pk=historic_result_two.pk
    ).is_in_companies_house is True
