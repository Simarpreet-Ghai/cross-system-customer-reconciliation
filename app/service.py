import json
import os
from collections import Counter
from pathlib import Path

import psycopg
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not set")


PROJECT_ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = PROJECT_ROOT / "sql"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


def run_sql_file(cursor, filename):
    sql_path = SQL_DIR / filename

    with sql_path.open() as file:
        query = file.read()

    cursor.execute(query)

    columns = [
        description.name
        for description in cursor.description
    ]

    rows = cursor.fetchall()

    return [
        dict(zip(columns, row))
        for row in rows
    ]


def run_reconciliation():
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO reconciliation_runs (status)
                VALUES ('RUNNING')
                RETURNING run_id;
                """
            )

            run_id = cursor.fetchone()[0]

            conn.commit()

            try:
                cursor.execute(
                    "SELECT COUNT(*) FROM system_a_customers;"
                )
                system_a_count = cursor.fetchone()[0]

                cursor.execute(
                    "SELECT COUNT(*) FROM system_b_customers;"
                )
                system_b_count = cursor.fetchone()[0]

                duplicates = run_sql_file(
                    cursor,
                    "02_detect_duplicates.sql",
                )

                missing = run_sql_file(
                    cursor,
                    "03_detect_missing_customers.sql",
                )

                mismatches = run_sql_file(
                    cursor,
                    "04_detect_field_mismatches.sql",
                )

                invalid_records = run_sql_file(
                    cursor,
                    "05_detect_invalid_records.sql",
                )

                issues = []

                for issue in duplicates:
                    issues.append({
                        "issue_type": issue["issue_type"],
                        "customer_id": issue["customer_id"],
                        "source_system": issue["source_system"],
                        "field": None,
                        "value_in_a": None,
                        "value_in_b": None,
                        "details": (
                            f"record_count={issue['record_count']}"
                        ),
                    })

                for issue in missing:
                    issues.append({
                        "issue_type": issue["issue_type"],
                        "customer_id": issue["customer_id"],
                        "source_system": None,
                        "field": None,
                        "value_in_a": None,
                        "value_in_b": None,
                        "details": None,
                    })

                for issue in mismatches:
                    issues.append({
                        "issue_type": issue["issue_type"],
                        "customer_id": issue["customer_id"],
                        "source_system": None,
                        "field": issue["field"],
                        "value_in_a": issue["value_in_a"],
                        "value_in_b": issue["value_in_b"],
                        "details": None,
                    })

                for issue in invalid_records:
                    issues.append({
                        "issue_type": issue["issue_type"],
                        "customer_id": issue["customer_id"],
                        "source_system": issue["source_system"],
                        "field": issue["field"],
                        "value_in_a": None,
                        "value_in_b": None,
                        "details": issue["reason"],
                    })

                for issue in issues:
                    cursor.execute(
                        """
                        INSERT INTO reconciliation_issues (
                            run_id,
                            issue_type,
                            customer_id,
                            source_system,
                            field,
                            value_in_a,
                            value_in_b,
                            details
                        )
                        VALUES (
                            %s, %s, %s, %s,
                            %s, %s, %s, %s
                        );
                        """,
                        (
                            run_id,
                            issue["issue_type"],
                            issue["customer_id"],
                            issue["source_system"],
                            issue["field"],
                            issue["value_in_a"],
                            issue["value_in_b"],
                            issue["details"],
                        ),
                    )

                cursor.execute(
                    """
                    UPDATE reconciliation_runs
                    SET
                        finished_at = CURRENT_TIMESTAMP,
                        status = 'COMPLETED',
                        system_a_record_count = %s,
                        system_b_record_count = %s,
                        issue_count = %s
                    WHERE run_id = %s;
                    """,
                    (
                        system_a_count,
                        system_b_count,
                        len(issues),
                        run_id,
                    ),
                )

                conn.commit()

                return {
                    "run_id": run_id,
                    "status": "COMPLETED",
                    "system_a_record_count": system_a_count,
                    "system_b_record_count": system_b_count,
                    "issue_count": len(issues),
                    "issues": issues,
                }

            except Exception:
                conn.rollback()

                cursor.execute(
                    """
                    UPDATE reconciliation_runs
                    SET
                        finished_at = CURRENT_TIMESTAMP,
                        status = 'FAILED'
                    WHERE run_id = %s;
                    """,
                    (run_id,),
                )

                conn.commit()

                raise


def save_report(result):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    issue_counts = Counter(
        issue["issue_type"]
        for issue in result["issues"]
    )

    report = {
        "run_id": result["run_id"],
        "status": result["status"],
        "source_record_counts": {
            "system_a": result["system_a_record_count"],
            "system_b": result["system_b_record_count"],
        },
        "summary": {
            "missing_in_a": issue_counts["MISSING_IN_A"],
            "missing_in_b": issue_counts["MISSING_IN_B"],
            "duplicates": issue_counts["DUPLICATE"],
            "field_mismatches": issue_counts["FIELD_MISMATCH"],
            "invalid_records": issue_counts["INVALID_RECORD"],
            "total_issues": result["issue_count"],
        },
        "issues": result["issues"],
    }

    report_path = (
        OUTPUT_DIR
        / f"reconciliation_report_{result['run_id']}.json"
    )

    with report_path.open("w") as file:
        json.dump(report, file, indent=4)

    return report_path


if __name__ == "__main__":
    result = run_reconciliation()
    report_path = save_report(result)

    print(f"Run ID: {result['run_id']}")
    print(f"Status: {result['status']}")
    print(
        f"System A records: "
        f"{result['system_a_record_count']}"
    )
    print(
        f"System B records: "
        f"{result['system_b_record_count']}"
    )
    print(f"Issues found: {result['issue_count']}")
    print(f"Report saved to: {report_path}")