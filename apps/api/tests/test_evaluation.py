from evals.runners.score_scenarios import run_regression


def test_regression_scores_seed_scenarios() -> None:
    report = run_regression()
    assert [entry["incidentId"] for entry in report] == [
        "deployment-breaks-auth-flow",
        "latency-spike-after-cache-config-change",
        "queue-workers-fail-after-dependency-upgrade",
    ]
    assert all(entry["evaluationScore"] >= 90.0 for entry in report)
