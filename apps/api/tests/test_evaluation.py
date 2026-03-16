from evals.runners.score_scenarios import run_regression


def test_regression_scores_seed_scenario() -> None:
    report = run_regression()
    assert report == [{"incidentId": "inc-auth-001", "evaluationScore": 100.0}]
