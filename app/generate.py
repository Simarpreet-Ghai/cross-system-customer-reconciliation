import json
from copy import deepcopy
from datetime import datetime
from pathlib import Path

from faker import Faker

FAKER_SEED = 42

STATUSES = ("ACTIVE", "INACTIVE", "SUSPENDED")


def generate_base_customers(count=100):
    fake = Faker()
    fake.seed_instance(FAKER_SEED)

    customers = []

    for number in range(1, count + 1):
        customer = {
            "customer_id": f"CUST-{number:05d}",
            "name": fake.name(),
            "email": fake.email(),
            "city": fake.city(),
            "status": fake.random_element(elements=STATUSES),
            "updated_at": fake.date_time_between(
                start_date=datetime(2024, 1, 1),
                end_date=datetime(2026, 8, 1),
            ),
        }

        customers.append(customer)

    return customers

def find_customer(customers, customer_id):
    for customer in customers:
        if customer["customer_id"] == customer_id:
            return customer

    raise ValueError(f"Customer {customer_id} not found")


def create_source_datasets(count=100):
    base_customers = generate_base_customers(count)

    system_a = deepcopy(base_customers)
    system_b = deepcopy(base_customers)

    return system_a, system_b


def seed_anomalies(system_a, system_b):
    manifest = {
        "missing_in_a": [],
        "missing_in_b": [],
        "duplicates": [],
        "field_mismatches": [],
        "invalid_records": [],
    }

    # Customer exists in B but is missing from A
    missing_in_a_id = "CUST-00010"
    system_a = [
        customer
        for customer in system_a
        if customer["customer_id"] != missing_in_a_id
    ]

    manifest["missing_in_a"].append(missing_in_a_id)

    # Customer exists in A but is missing from B
    missing_in_b_id = "CUST-00020"
    system_b = [
        customer
        for customer in system_b
        if customer["customer_id"] != missing_in_b_id
    ]

    manifest["missing_in_b"].append(missing_in_b_id)

    # Duplicate customer in System A
    duplicate_id = "CUST-00030"
    duplicate_customer = deepcopy(
        find_customer(system_a, duplicate_id)
    )

    system_a.append(duplicate_customer)

    manifest["duplicates"].append(
        {
            "customer_id": duplicate_id,
            "system": "A",
            "expected_count": 2,
        }
    )

    # Same customer, different city
    mismatch_id = "CUST-00040"

    customer_a = find_customer(system_a, mismatch_id)
    customer_b = find_customer(system_b, mismatch_id)

    customer_a["city"] = "Toronto"
    customer_b["city"] = "Ottawa"

    manifest["field_mismatches"].append(
        {
            "customer_id": mismatch_id,
            "field": "city",
            "value_in_a": "Toronto",
            "value_in_b": "Ottawa",
        }
    )

    # Invalid email in System B
    invalid_id = "CUST-00050"
    invalid_customer = find_customer(system_b, invalid_id)

    invalid_customer["email"] = "not-an-email"

    manifest["invalid_records"].append(
        {
            "customer_id": invalid_id,
            "system": "B",
            "field": "email",
            "reason": "malformed_email",
            "value": "not-an-email",
        }
    )

    return system_a, system_b, manifest


def save_manifest(manifest, path="data/generated/manifest.json"):
    output_path = Path(path)

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w") as file:
        json.dump(manifest, file, indent=4)


if __name__ == "__main__":
    system_a, system_b = create_source_datasets(100)

    system_a, system_b, manifest = seed_anomalies(
        system_a,
        system_b,
    )
    
    save_manifest(manifest)