-- Data quality checks on newly ingested data
WITH new_data AS (
    SELECT *
    FROM CITIBIKE_DB.EXTERNAL.V_TRIPS_RAW
    WHERE source_file LIKE '%{{ ti.xcom_pull(task_ids='download_data', key='year') }}{{ ti.xcom_pull(task_ids='download_data', key='month') | string | rjust(2, '0') }}%'
)
SELECT
    COUNT(*) AS total_rows,
    COUNT(DISTINCT ride_id) AS unique_rides,
    COUNT(*) - COUNT(ride_id) AS null_ride_ids,
    COUNT(*) - COUNT(started_at) AS null_started_at,
    COUNT(*) - COUNT(start_station_id) AS null_start_station,
    MIN(started_at) AS earliest_trip,
    MAX(started_at) AS latest_trip,
    CASE 
        WHEN COUNT(*) < {{ params.min_rows }} THEN 'FAIL: Too few rows'
        WHEN COUNT(*) - COUNT(ride_id) > COUNT(*) * 0.01 THEN 'FAIL: Too many null ride_ids'
        WHEN COUNT(*) - COUNT(started_at) > COUNT(*) * 0.01 THEN 'FAIL: Too many null timestamps'
        ELSE 'PASS'
    END AS quality_status
FROM new_data;