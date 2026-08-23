import psycopg


def test_test_database_has_expected_tables(test_database):
    with psycopg.connect(test_database) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public';
                """
            )

            tables = {
                row[0]
                for row in cursor.fetchall()
            }

    expected_tables = {
        "system_a_customers",
        "system_b_customers",
        "reconciliation_runs",
        "reconciliation_issues",
    }

    assert expected_tables.issubset(tables)