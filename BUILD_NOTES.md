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