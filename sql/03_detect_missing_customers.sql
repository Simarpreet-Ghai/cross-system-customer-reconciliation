WITH unique_a AS (
    SELECT customer_id
    FROM system_a_customers
    WHERE customer_id IS NOT NULL
      AND BTRIM(customer_id) <> ''
    GROUP BY customer_id
    HAVING COUNT(*) = 1
),
unique_b AS (
    SELECT customer_id
    FROM system_b_customers
    WHERE customer_id IS NOT NULL
      AND BTRIM(customer_id) <> ''
    GROUP BY customer_id
    HAVING COUNT(*) = 1
)

SELECT
    'MISSING_IN_B' AS issue_type,
    a.customer_id
FROM unique_a AS a
WHERE NOT EXISTS (
    SELECT 1
    FROM system_b_customers AS b
    WHERE b.customer_id = a.customer_id
)

UNION ALL

SELECT
    'MISSING_IN_A' AS issue_type,
    b.customer_id
FROM unique_b AS b
WHERE NOT EXISTS (
    SELECT 1
    FROM system_a_customers AS a
    WHERE a.customer_id = b.customer_id
)

ORDER BY customer_id;