"""The four DORA metrics: deployment frequency, lead time for changes,
change failure rate, and time to restore service."""
from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import median


@dataclass
class Deployment:
    deployed_at: datetime
    committed_at: datetime          # first commit in the change
    failed: bool
    restored_at: datetime | None    # when service recovered, if it failed


def _ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def load_csv(path: str | Path) -> list[Deployment]:
    out = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            out.append(Deployment(
                deployed_at=_ts(row["deployed_at"]),
                committed_at=_ts(row["committed_at"]),
                failed=row["failed"].strip().lower() in ("true", "1", "yes"),
                restored_at=_ts(row["restored_at"]) if row.get("restored_at") else None,
            ))
    return sorted(out, key=lambda d: d.deployed_at)


def deployment_frequency(deps: list[Deployment]) -> float:
    """Deployments per day across the observed window."""
    if len(deps) < 2:
        return float(len(deps))
    days = (deps[-1].deployed_at - deps[0].deployed_at).total_seconds() / 86400
    return len(deps) / max(days, 1)


def lead_time_hours(deps: list[Deployment]) -> float:
    """Median hours from first commit to production."""
    return median((d.deployed_at - d.committed_at).total_seconds() / 3600 for d in deps)


def change_failure_rate(deps: list[Deployment]) -> float:
    return sum(d.failed for d in deps) / len(deps)


def time_to_restore_hours(deps: list[Deployment]) -> float | None:
    """Median hours from a failed deploy to recovery. None if nothing failed."""
    durations = [(d.restored_at - d.deployed_at).total_seconds() / 3600
                 for d in deps if d.failed and d.restored_at]
    return median(durations) if durations else None


def performance_tier(freq_per_day: float, lead_hours: float, cfr: float, ttr: float | None) -> str:
    """Rough tier based on the DORA research bands."""
    ttr = ttr if ttr is not None else 0
    if freq_per_day >= 1 and lead_hours <= 24 and cfr <= 0.15 and ttr <= 1:
        return "elite"
    if freq_per_day >= 1 / 7 and lead_hours <= 24 * 7 and cfr <= 0.20 and ttr <= 24:
        return "high"
    if freq_per_day >= 1 / 30 and lead_hours <= 24 * 30 and cfr <= 0.30 and ttr <= 24 * 7:
        return "medium"
    return "low"


def summarize(deps: list[Deployment]) -> dict:
    freq = deployment_frequency(deps)
    lead = lead_time_hours(deps)
    cfr = change_failure_rate(deps)
    ttr = time_to_restore_hours(deps)
    return {
        "deployments": len(deps),
        "deploys_per_day": round(freq, 2),
        "median_lead_time_hours": round(lead, 1),
        "change_failure_rate": round(cfr, 3),
        "median_time_to_restore_hours": None if ttr is None else round(ttr, 1),
        "tier": performance_tier(freq, lead, cfr, ttr),
    }
