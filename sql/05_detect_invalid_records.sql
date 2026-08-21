WITH all_customers AS (
    SELECT
        'A' AS source_system,
        customer_id,
        email,
        status
    FROM system_a_customers

    UNION ALL

    SELECT
        'B' AS source_system,
        customer_id,
        email,
        status
    FROM system_b_customers
)

SELECT
    'INVALID_RECORD' AS issue_type,
    source_system,
    customer_id,

    CASE
        WHEN customer_id IS NULL OR BTRIM(customer_id) = ''
            THEN 'customer_id'
        WHEN email IS NULL OR BTRIM(email) = ''
            THEN 'email'
        WHEN email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'
            THEN 'email'
        WHEN status IS NULL
             OR status NOT IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')
            THEN 'status'
    END AS field,

    CASE
        WHEN customer_id IS NULL OR BTRIM(customer_id) = ''
            THEN 'missing_customer_id'
        WHEN email IS NULL OR BTRIM(email) = ''
            THEN 'missing_email'
        WHEN email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'
            THEN 'malformed_email'
        WHEN status IS NULL
             OR status NOT IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')
            THEN 'invalid_status'
    END AS reason

FROM all_customers

WHERE customer_id IS NULL
   OR BTRIM(customer_id) = ''
   OR email IS NULL
   OR BTRIM(email) = ''
   OR email !~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'
   OR status IS NULL
   OR status NOT IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')

ORDER BY source_system, customer_id;