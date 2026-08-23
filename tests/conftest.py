import os
from pathlib import Path

import psycopg
import pytest
from dotenv import load_dotenv


load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError("TEST_DATABASE_URL is not set")


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = PROJECT_ROOT / "sql"


@pytest.fixture
def test_database():
    with psycopg.connect(TEST_DATABASE_URL) as conn:
        if conn.info.dbname != "reconciliation_test":
            raise RuntimeError(
                "Tests must only run against reconciliation_test"
            )

        with conn.cursor() as cursor:
            cursor.execute(
                """
                DROP TABLE IF EXISTS reconciliation_issues;
                DROP TABLE IF EXISTS reconciliation_runs;
                DROP TABLE IF EXISTS system_a_customers;
                DROP TABLE IF EXISTS system_b_customers;
                """
            )

            schema_files = [
                "01_create_source_tables.sql",
                "06_create_reconciliation_runs.sql",
                "07_create_reconciliation_issues.sql",
            ]

            for filename in schema_files:
                sql_path = SQL_DIR / filename

                with sql_path.open() as file:
                    cursor.execute(file.read())

        conn.commit()

    yield TEST_DATABASE_URL