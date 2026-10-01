from datetime import datetime, timedelta, timezone
from pathlib import Path

from dora.metrics import (Deployment, change_failure_rate, load_csv, performance_tier,
                          summarize, time_to_restore_hours)

T0 = datetime(2026, 9, 1, tzinfo=timezone.utc)


def dep(day, lead_h=4, failed=False, restore_h=None):
    at = T0 + timedelta(days=day)
    return Deployment(at, at - timedelta(hours=lead_h), failed,
                      at + timedelta(hours=restore_h) if restore_h else None)


def test_change_failure_rate():
    assert change_failure_rate([dep(0), dep(1, failed=True, restore_h=1)]) == 0.5


def test_no_failures_means_no_restore_time():
    assert time_to_restore_hours([dep(0), dep(1)]) is None


def test_elite_team():
    deps = [dep(i * 0.5, lead_h=2) for i in range(20)]
    assert summarize(deps)["tier"] == "elite"


def test_slow_team_is_low():
    assert performance_tier(1 / 90, 24 * 60, 0.5, 200) == "low"


def test_sample_file_loads():
    s = summarize(load_csv(Path(__file__).parent.parent / "data" / "sample_deployments.csv"))
    assert s["deployments"] == 10
    assert s["change_failure_rate"] == 0.2
