from app.generate import (
    create_source_datasets,
    generate_base_customers,
    seed_anomalies,
)


def test_generator_is_deterministic():
    first_run = generate_base_customers(10)
    second_run = generate_base_customers(10)

    assert first_run == second_run


def test_generated_customer_structure():
    customers = generate_base_customers(5)

    assert len(customers) == 5

    expected_fields = {
        "customer_id",
        "name",
        "email",
        "city",
        "status",
        "updated_at",
    }

    for customer in customers:
        assert set(customer.keys()) == expected_fields


def test_seeded_anomalies_match_manifest():
    system_a, system_b = create_source_datasets(100)
    system_a, system_b, manifest = seed_anomalies(
        system_a,
        system_b,
    )

    ids_a = [
        customer["customer_id"]
        for customer in system_a
    ]

    ids_b = [
        customer["customer_id"]
        for customer in system_b
    ]

    # Missing records
    assert "CUST-00010" not in ids_a
    assert "CUST-00010" in ids_b
    assert "CUST-00010" in manifest["missing_in_a"]

    assert "CUST-00020" in ids_a
    assert "CUST-00020" not in ids_b
    assert "CUST-00020" in manifest["missing_in_b"]

    # Duplicate
    assert ids_a.count("CUST-00030") == 2

    duplicate = manifest["duplicates"][0]
    assert duplicate["customer_id"] == "CUST-00030"
    assert duplicate["system"] == "A"
    assert duplicate["expected_count"] == 2

    # Field mismatch
    customer_a = next(
        customer
        for customer in system_a
        if customer["customer_id"] == "CUST-00040"
    )

    customer_b = next(
        customer
        for customer in system_b
        if customer["customer_id"] == "CUST-00040"
    )

    assert customer_a["city"] == "Toronto"
    assert customer_b["city"] == "Ottawa"

    mismatch = manifest["field_mismatches"][0]
    assert mismatch["customer_id"] == "CUST-00040"
    assert mismatch["field"] == "city"
    assert mismatch["value_in_a"] == "Toronto"
    assert mismatch["value_in_b"] == "Ottawa"

    # Invalid record
    invalid_customer = next(
        customer
        for customer in system_b
        if customer["customer_id"] == "CUST-00050"
    )

    assert invalid_customer["email"] == "not-an-email"

    invalid = manifest["invalid_records"][0]
    assert invalid["customer_id"] == "CUST-00050"
    assert invalid["system"] == "B"
    assert invalid["field"] == "email"
    assert invalid["reason"] == "malformed_email"