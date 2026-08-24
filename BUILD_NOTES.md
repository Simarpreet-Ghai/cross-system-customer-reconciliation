## 2026-08-18

What I worked on:
Made the Faker customer generator deterministic.

Problem encountered / why:
Faker raised an error when I passed date boundaries as strings to `date_time_between()`.

How I fixed it:
Replaced the string dates with explicit Python `datetime` objects.

What I learned:
Using fixed seeds, pinned Faker versions, and fixed date ranges makes generated test data reproducible.

### Customer data-quality rules

- Allowed statuses: ACTIVE, INACTIVE, SUSPENDED
- Email is required and must follow a basic valid email format
- customer_id is required

### PostgreSQL data loading

What I worked on:
Added a loader that generates the two customer datasets and loads them into PostgreSQL.

What I verified:
The loader can be rerun without stacking old data, and the database contains the expected missing records, duplicate, field mismatch, and invalid email.

What I learned:
Using one transaction keeps the table reset and inserts together, so a failed load does not leave the database partially updated.

### Reconciliation rules

- MISSING_IN_A: customer exists in System B but not System A
- MISSING_IN_B: customer exists in System A but not System B
- DUPLICATE: the same customer_id appears more than once in one system
- FIELD_MISMATCH: the customer exists in both systems but a comparable field is different
- INVALID_RECORD: the record violates one of the defined customer data-quality rules

### Record eligibility

- A missing or blank customer_id is reported as INVALID_RECORD and excluded from cross-system matching.
- A duplicate customer_id is reported as DUPLICATE and excluded from normal one-to-one field comparison.
- A valid, unique customer_id can be used for missing-record checks.
- Records that fail email or status validation are reported as INVALID_RECORD and excluded from field-mismatch comparison.

### Reproducibility check

What happened:
A fresh clone worked through setup, loading, and reconciliation, but the database tests failed when I used a test database with a different name.

Problem encountered / why:
The pytest database fixture only allowed a database named exactly `reconciliation_test`, which made the setup unnecessarily machine-specific.

How I fixed it:
Changed the safety check to allow any database name ending in `_test` while still blocking development databases.

What I learned:
Reproducing a project from a clean clone can expose assumptions that are hidden on the original development machine.