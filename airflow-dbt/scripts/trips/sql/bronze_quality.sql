-- Data quality checks on newly ingested data
-- This query succeeds silently when quality passes,
-- and raises a division-by-zero error when quality fails,
-- which causes SQLExecuteQueryOperator to fail the task.
WITH new_data AS (
    SELECT *
    FROM CITIBIKE_DB.EXTERNAL.V_TRIPS_RAW
    WHERE source_file LIKE '%{{ ti.xcom_pull(task_ids='ingest_trips_data', key='year') }}{{ ti.xcom_pull(task_ids='ingest_trips_data', key='month') | string | rjust(2, '0') }}%'
),
quality_checks AS (
    SELECT
        COUNT(*)                                    AS total_rows,
        COUNT(DISTINCT ride_id)                     AS unique_rides,
        COUNT(*) - COUNT(ride_id)                   AS null_ride_ids,
        COUNT(*) - COUNT(started_at)                AS null_started_at,
        COUNT(*) - COUNT(start_station_id)          AS null_start_station,
        MIN(started_at)                             AS earliest_trip,
        MAX(started_at)                             AS latest_trip
    FROM new_data
),
validation AS (
    SELECT
        *,
        CASE
            WHEN total_rows < {{ params.min_rows }}
                THEN 'FAIL: Too few rows (' || total_rows || ' < {{ params.min_rows }})'
            WHEN null_ride_ids > total_rows * 0.01
                THEN 'FAIL: Too many null ride_ids (' || null_ride_ids || ')'
            WHEN null_started_at > total_rows * 0.01
                THEN 'FAIL: Too many null timestamps (' || null_started_at || ')'
            ELSE 'PASS'
        END AS quality_status
    FROM quality_checks
)
SELECT
    total_rows,
    unique_rides,
    null_ride_ids,
    null_started_at,
    null_start_station,
    earliest_trip,
    latest_trip,
    quality_status,
    -- Force a division-by-zero error when quality_status != 'PASS'
    -- This makes the SQLExecuteQueryOperator fail the task
    1 / IFF(quality_status = 'PASS', 1, 0) AS assertion
FROM validation;
