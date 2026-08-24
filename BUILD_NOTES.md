# Build Notes

These are a few notes I kept while building the project, mostly around problems I ran into, design decisions, and things I wanted to remember later.

## 2026-08-18

### Deterministic Customer Generation

**What I worked on:** Made the Faker customer generator deterministic.

**Problem encountered / why:** Faker raised an error when I passed date boundaries as strings to `date_time_between()`.

**How I fixed it:** Replaced the string dates with explicit Python `datetime` objects.

**What I learned:** Using fixed seeds, pinned Faker versions, and fixed date ranges makes generated test data reproducible.

### Customer Data-Quality Rules

- Allowed statuses: `ACTIVE`, `INACTIVE`, `SUSPENDED`
- Email is required and must follow a basic valid email format
- `customer_id` is required

### PostgreSQL Data Loading

**What I worked on:** Added a loader that generates the two customer datasets and loads them into PostgreSQL.

**What I verified:** The loader can be rerun without stacking old data, and the database contains the expected missing records, duplicate, field mismatch, and invalid email.

**What I learned:** Using one transaction keeps the table reset and inserts together, so a failed load does not leave the database partially updated.

---

## 2026-08-21

### Reconciliation Rules

I added the SQL checks used to find the different types of inconsistencies between the two systems.

- `MISSING_IN_A`: customer exists in System B but not System A
- `MISSING_IN_B`: customer exists in System A but not System B
- `DUPLICATE`: the same `customer_id` appears more than once in one system
- `FIELD_MISMATCH`: the customer exists in both systems but a comparable field is different
- `INVALID_RECORD`: the record violates one of the defined customer data-quality rules

### Record Eligibility

I also had to decide which records should be allowed into each reconciliation check.

- A missing or blank `customer_id` is reported as `INVALID_RECORD` and excluded from cross-system matching.
- A duplicate `customer_id` is reported as `DUPLICATE` and excluded from normal one-to-one field comparison.
- A valid, unique `customer_id` can be used for missing-record checks.
- Records that fail email or status validation are reported as `INVALID_RECORD` and excluded from field-mismatch comparison.

**What I learned:** Separating invalid and duplicate records before normal comparison helps prevent the same bad record from being reported multiple ways.

---

## 2026-08-22

### Reconciliation History and Reporting

**What I worked on:** Added tables for reconciliation runs and issues, then connected the SQL checks through a Python reconciliation service.

Each run now stores information such as:

- run status
- System A record count
- System B record count
- total issue count
- individual issue details

The service also creates a JSON report containing a summary and the detected issues.

**What I learned:** Saving each run separately makes it possible to keep an audit history instead of losing the reconciliation results when the program finishes.

---

## 2026-08-23

### Automated Testing

**What I worked on:** Added automated tests for the data generator, test database setup, and reconciliation results.

The most important test compares the inconsistencies I intentionally seeded into the data with the issues the reconciliation engine actually detects.

**What I verified:** All 5 automated tests pass, including the ground-truth check confirming that the reconciliation engine detects all 5 expected seeded issues.

**What I learned:** Keeping the expected problems separate from the reconciliation logic gives me a way to verify the engine without relying on manual inspection.

---

## 2026-08-24

### Reproducibility Check

**What happened:** I tested the project from a fresh clone. Setup, loading, and reconciliation worked, but the database tests failed when I used a test database with a different name.

**Problem encountered / why:** The pytest database fixture only allowed a database named exactly `reconciliation_test`, which made the setup unnecessarily machine-specific.

**How I fixed it:** Changed the safety check to allow any database name ending in `_test` while still blocking development databases.

**What I learned:** Reproducing a project from a clean clone can expose assumptions that are hidden on the original development machine.
