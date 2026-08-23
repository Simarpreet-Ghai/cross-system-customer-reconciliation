from app.generate import (
    create_source_datasets,
    seed_anomalies,
)
from app.load import load_customer_data
from app.service import run_reconciliation


def test_reconciliation_matches_seeded_anomalies(test_database):
    system_a, system_b = create_source_datasets(100)

    _, _, manifest = seed_anomalies(
        system_a,
        system_b,
    )

    load_customer_data(test_database)

    result = run_reconciliation(test_database)

    expected_issues = set()

    for customer_id in manifest["missing_in_a"]:
        expected_issues.add(
            (
                "MISSING_IN_A",
                customer_id,
                None,
                None,
                None,
                None,
                None,
            )
        )

    for customer_id in manifest["missing_in_b"]:
        expected_issues.add(
            (
                "MISSING_IN_B",
                customer_id,
                None,
                None,
                None,
                None,
                None,
            )
        )

    for issue in manifest["duplicates"]:
        expected_issues.add(
            (
                "DUPLICATE",
                issue["customer_id"],
                issue["system"],
                None,
                None,
                None,
                f"record_count={issue['expected_count']}",
            )
        )

    for issue in manifest["field_mismatches"]:
        expected_issues.add(
            (
                "FIELD_MISMATCH",
                issue["customer_id"],
                None,
                issue["field"],
                issue["value_in_a"],
                issue["value_in_b"],
                None,
            )
        )

    for issue in manifest["invalid_records"]:
        expected_issues.add(
            (
                "INVALID_RECORD",
                issue["customer_id"],
                issue["system"],
                issue["field"],
                None,
                None,
                issue["reason"],
            )
        )

    actual_issues = {
        (
            issue["issue_type"],
            issue["customer_id"],
            issue["source_system"],
            issue["field"],
            issue["value_in_a"],
            issue["value_in_b"],
            issue["details"],
        )
        for issue in result["issues"]
    }

    assert actual_issues == expected_issues