# Project Metrics

I wanted to keep track of a few real numbers from the project so I can use them later without guessing or exaggerating anything.

## Seeded Anomaly Detection

I intentionally added 5 known problems into the generated customer data:

- 1 customer missing from System A
- 1 customer missing from System B
- 1 duplicate customer
- 1 field mismatch
- 1 invalid record

The reconciliation engine detected all 5.

```text
5/5 seeded anomalies detected
100%
