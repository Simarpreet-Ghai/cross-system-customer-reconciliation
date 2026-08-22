CREATE TABLE reconciliation_issues (
    issue_id BIGSERIAL PRIMARY KEY,
    run_id BIGINT NOT NULL
        REFERENCES reconciliation_runs(run_id)
        ON DELETE CASCADE,
    issue_type VARCHAR(30) NOT NULL,
    customer_id VARCHAR(20),
    source_system VARCHAR(1),
    field VARCHAR(100),
    value_in_a TEXT,
    value_in_b TEXT,
    details TEXT
);