SELECT
    'DUPLICATE' AS issue_type,
    'A' AS source_system,
    customer_id,
    COUNT(*) AS record_count
FROM system_a_customers
WHERE customer_id IS NOT NULL
  AND BTRIM(customer_id) <> ''
GROUP BY customer_id
HAVING COUNT(*) > 1

UNION ALL

SELECT
    'DUPLICATE' AS issue_type,
    'B' AS source_system,
    customer_id,
    COUNT(*) AS record_count
FROM system_b_customers
WHERE customer_id IS NOT NULL
  AND BTRIM(customer_id) <> ''
GROUP BY customer_id
HAVING COUNT(*) > 1

ORDER BY customer_id, source_system;