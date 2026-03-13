-- Test: Trip duration distribution should be reasonable

WITH duration_stats AS (
    SELECT
        COUNT(*) AS total_trips,
        AVG(trip_duration_seconds) AS avg_duration,
        MEDIAN(trip_duration_seconds) AS median_duration,
        PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY trip_duration_seconds) AS p95_duration
    FROM {{ ref('fact_trips') }}
    WHERE start_time >= DATEADD('month', -1, CURRENT_DATE())
)

SELECT *
FROM duration_stats
WHERE 
    avg_duration NOT BETWEEN 300 AND 3600  -- 5-60 min average
    OR median_duration NOT BETWEEN 240 AND 1800  -- 4-30 min median
    OR p95_duration > 7200  -- 95th percentile should be < 2 hours