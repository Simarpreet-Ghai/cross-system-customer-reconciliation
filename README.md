# Cross-System Customer Reconciliation

I built this project to learn more about Python, PostgreSQL, SQL, and data-quality problems by simulating two customer systems that are supposed to contain the same information but slowly drift apart.

The project generates synthetic customer records, intentionally adds a few inconsistencies, loads both systems into PostgreSQL, and then detects and records the differences.

## What It Detects

The reconciliation logic currently finds:

- customers missing from System A
- customers missing from System B
- duplicate customer IDs
- mismatched customer fields
- invalid records

The current generated data intentionally includes examples of each problem so I know what the program is supposed to find.

For example:

```text
CUST-00010 → missing from System A
CUST-00020 → missing from System B
CUST-00030 → duplicate in System A
CUST-00040 → city mismatch
CUST-00050 → invalid email
```

## How It Works

```text
Synthetic customer data
        |
        v
 System A + System B
        |
        v
     PostgreSQL
        |
        v
 SQL reconciliation checks
        |
        v
   Python service
        |
   +----+----+
   |         |
   v         v
Audit data  JSON report
        |
        v
      pytest
```

Python handles the overall workflow, while SQL handles most of the actual record comparison.

Each reconciliation run is also saved in PostgreSQL so previous runs and their detected issues can still be viewed later.

## Tech Used

- **Python** — data generation, loading, reconciliation workflow, and reporting
- **PostgreSQL** — stores both customer systems and reconciliation history
- **SQL** — detects duplicates, missing records, mismatches, and invalid data
- **Psycopg** — connects Python to PostgreSQL
- **Faker** — generates reproducible synthetic customer data
- **pytest** — checks that the generated problems match what the reconciliation engine detects

## Project Structure

```text
app/
├── generate.py
├── load.py
└── service.py

sql/
├── 01_create_source_tables.sql
├── 02_detect_duplicates.sql
├── 03_detect_missing_customers.sql
├── 04_detect_field_mismatches.sql
├── 05_detect_invalid_records.sql
├── 06_create_reconciliation_runs.sql
└── 07_create_reconciliation_issues.sql

tests/
├── conftest.py
├── test_database.py
├── test_generate.py
└── test_ground_truth.py
```

## A Few Design Choices

One decision I made was to keep the PostgreSQL row `id` separate from `customer_id`.

That way, duplicate customer IDs can actually exist in the source data and be detected by the reconciliation logic instead of PostgreSQL rejecting them first.

I also made duplicate and invalid records get handled before normal field comparisons. This avoids one bad record creating several misleading issues.

## How to Run It on Another Computer

### 1. Requirements

You will need:

- Python
- PostgreSQL
- Git

### 2. Clone the repository

```bash
git clone <repository-url>
cd cross-system-customer-reconciliation
```

### 3. Create a virtual environment

```bash
python -m venv .venv
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

On Windows:

```bash
.venv\Scripts\activate
```

### 4. Install the Python packages

```bash
pip install -r requirements.txt
```

### 5. Create the databases

```bash
createdb reconciliation
createdb reconciliation_test
```

`reconciliation` is used for normal runs.

`reconciliation_test` is kept separate so the automated tests can safely reset their own data.

### 6. Set up environment variables

Create a `.env` file based on `.env.example`.

Example:

```env
DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/reconciliation
TEST_DATABASE_URL=postgresql://USER:PASSWORD@localhost:5432/reconciliation_test
```

Replace `USER` and `PASSWORD` with your local PostgreSQL information.

### 7. Create the PostgreSQL tables

```bash
psql reconciliation -f sql/01_create_source_tables.sql
psql reconciliation -f sql/06_create_reconciliation_runs.sql
psql reconciliation -f sql/07_create_reconciliation_issues.sql
```

### 8. Load the generated customer data

```bash
python -m app.load
```

### 9. Run the reconciliation

```bash
python -m app.service
```

A run should print something similar to:

```text
Run ID: 2
Status: COMPLETED
System A records: 100
System B records: 99
Issues found: 5
```

A JSON report is also created inside:

```text
data/output/
```

## Testing

Run:

```bash
python -m pytest -v
```

Right now there are 5 automated tests.

The most important one compares:

```text
problems intentionally added to the data
                vs
problems detected by the reconciliation engine
```

This lets me check automatically that the reconciliation result matches the known generated data instead of only checking the SQL output manually.

Current result:

```text
5 passed
```

## What I Learned

This project gave me more practice with:

- writing SQL for real comparison logic instead of only basic CRUD queries
- working with PostgreSQL from Python
- database transactions
- designing reproducible test data
- keeping audit history between program runs
- separating SQL detection logic from Python application logic
- testing a workflow that uses an actual database

## Current Limitations

Right now:

- customer matching uses exact IDs
- the project uses synthetic data
- field comparisons are exact
- reconciliation is started from the command line

I kept the first version focused on getting the main reconciliation and testing logic working properly before adding more features.

## Possible Next Steps

Things I may add later:

- FastAPI endpoints for starting and viewing reconciliation runs
- Docker for easier setup
- fuzzy matching
- GitHub Actions to run the tests automatically