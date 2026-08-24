# Project Metrics

These are measurements taken from the current deterministic project data and automated tests.

## Seeded Anomaly Detection

Metric: Seeded anomalies correctly detected

Result: 5/5 (100%)

How measured:
The ground-truth pytest test compares the issues intentionally planted by the data generator against the issues returned by the reconciliation engine.

Command:

```bash
python -m pytest tests/test_ground_truth.py -v