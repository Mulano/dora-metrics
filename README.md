# dora-metrics

Computes the four DORA delivery metrics from a simple deployment log and places the team in a performance tier.

| Metric | Question it answers |
|---|---|
| Deployment frequency | How often do we ship? |
| Lead time for changes | How long from first commit to production? |
| Change failure rate | What share of deploys cause a failure? |
| Time to restore | How fast do we recover when one does? |

## Run it
```bash
python -m dora.cli data/sample_deployments.csv
pip install pytest && pytest -q
```

Input is a CSV with `deployed_at`, `committed_at`, `failed`, and `restored_at` (ISO timestamps). Export it from your CI system or deployment tool.

## Design choices
- **Medians, not means**, for lead time and restore time, so one stuck change doesn't distort the picture.
- **Failures without a recovery time are counted in the failure rate** but excluded from restore time instead of being guessed.
- Tier thresholds follow the bands published in the DORA research; treat them as a rough guide, not a grade.

## What I'd add next
- Pull deployments directly from the GitHub Actions or GitLab API
- Split metrics by delivery lane (agentic vs. human-reviewed) to see whether automation actually helps
- A weekly trend chart
