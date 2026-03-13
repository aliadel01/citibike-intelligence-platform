-- Test: Daily trip counts should be within reasonable bounds

WITH daily_counts AS (
    SELECT 
        DATE(start_time) AS trip_date,
        COUNT(*) AS trip_count
    FROM {{ ref('fact_trips') }}
    WHERE start_time >= DATEADD('month', -3, CURRENT_DATE())
    GROUP BY 1
)

SELECT
    trip_date,
    trip_count
FROM daily_counts
WHERE 
    trip_count < 1000  -- Too low (system issue?)
    OR trip_count > 200000  -- Too high (data issue?)