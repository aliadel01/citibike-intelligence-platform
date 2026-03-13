{% macro test_row_count_change(model, threshold_percent=20) %}

WITH current_count AS (
    SELECT COUNT(*) AS row_count
    FROM {{ model }}
),

previous_count AS (
    SELECT {{ threshold_percent }} AS threshold_pct
)

SELECT 
    row_count,
    LAG(row_count) OVER (ORDER BY 1) AS previous_count,
    CASE 
        WHEN previous_count IS NULL THEN 0
        ELSE ABS((row_count - previous_count) * 100.0 / previous_count)
    END AS percent_change
FROM current_count
WHERE percent_change > (SELECT threshold_pct FROM previous_count)

{% endmacro %}