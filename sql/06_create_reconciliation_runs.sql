CREATE TABLE reconciliation_runs (
    run_id BIGSERIAL PRIMARY KEY,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    status VARCHAR(20) NOT NULL,
    system_a_record_count INTEGER,
    system_b_record_count INTEGER,
    issue_count INTEGER NOT NULL DEFAULT 0
);