WITH a_counts AS (
    SELECT customer_id, COUNT(*) AS record_count
    FROM system_a_customers
    WHERE customer_id IS NOT NULL
      AND BTRIM(customer_id) <> ''
    GROUP BY customer_id
),
b_counts AS (
    SELECT customer_id, COUNT(*) AS record_count
    FROM system_b_customers
    WHERE customer_id IS NOT NULL
      AND BTRIM(customer_id) <> ''
    GROUP BY customer_id
)

SELECT
    'FIELD_MISMATCH' AS issue_type,
    a.customer_id,
    difference.field,
    difference.value_in_a,
    difference.value_in_b
FROM system_a_customers AS a
JOIN system_b_customers AS b
    ON a.customer_id = b.customer_id
JOIN a_counts AS ac
    ON a.customer_id = ac.customer_id
JOIN b_counts AS bc
    ON b.customer_id = bc.customer_id

CROSS JOIN LATERAL (
    VALUES
        ('name', a.name::text, b.name::text),
        ('email', a.email::text, b.email::text),
        ('city', a.city::text, b.city::text),
        ('status', a.status::text, b.status::text),
        ('updated_at', a.updated_at::text, b.updated_at::text)
) AS difference(field, value_in_a, value_in_b)

WHERE ac.record_count = 1
  AND bc.record_count = 1

  AND a.email IS NOT NULL
  AND BTRIM(a.email) <> ''
  AND a.email ~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'

  AND b.email IS NOT NULL
  AND BTRIM(b.email) <> ''
  AND b.email ~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'

  AND a.status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')
  AND b.status IN ('ACTIVE', 'INACTIVE', 'SUSPENDED')

  AND difference.value_in_a IS DISTINCT FROM difference.value_in_b

ORDER BY a.customer_id, difference.field;