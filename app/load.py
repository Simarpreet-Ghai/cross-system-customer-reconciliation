import os

import psycopg
from dotenv import load_dotenv

from app.generate import (
    create_source_datasets,
    save_manifest,
    seed_anomalies,
)


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


def customer_rows(customers):
    return [
        (
            customer["customer_id"],
            customer["name"],
            customer["email"],
            customer["city"],
            customer["status"],
            customer["updated_at"],
        )
        for customer in customers
    ]


def load_customer_data():
    system_a, system_b = create_source_datasets(100)

    system_a, system_b, manifest = seed_anomalies(
        system_a,
        system_b,
    )

    rows_a = customer_rows(system_a)
    rows_b = customer_rows(system_b)

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                TRUNCATE TABLE
                    system_a_customers,
                    system_b_customers
                RESTART IDENTITY;
                """
            )

            cursor.executemany(
                """
                INSERT INTO system_a_customers
                    (customer_id, name, email, city, status, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                rows_a,
            )

            cursor.executemany(
                """
                INSERT INTO system_b_customers
                    (customer_id, name, email, city, status, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s);
                """,
                rows_b,
            )

    save_manifest(manifest)

    print(f"Loaded {len(system_a)} records into System A")
    print(f"Loaded {len(system_b)} records into System B")


if __name__ == "__main__":
    load_customer_data()