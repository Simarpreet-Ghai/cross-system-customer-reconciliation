CREATE TABLE system_a_customers (
    id BIGSERIAL PRIMARY KEY,
    customer_id VARCHAR(20),
    name VARCHAR(100),
    email VARCHAR(255),
    city VARCHAR(100),
    status VARCHAR(20),
    updated_at TIMESTAMP
);

CREATE TABLE system_b_customers (
    id BIGSERIAL PRIMARY KEY,
    customer_id VARCHAR(20),
    name VARCHAR(100),
    email VARCHAR(255),
    city VARCHAR(100),
    status VARCHAR(20),
    updated_at TIMESTAMP
);