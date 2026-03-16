-- Refresh external table metadata
ALTER EXTERNAL TABLE CITIBIKE_DB.EXTERNAL.V_TRIPS_RAW REFRESH;

-- Verify row count
SELECT COUNT(*) AS row_count 
FROM CITIBIKE_DB.EXTERNAL.V_TRIPS_RAW
WHERE source_file LIKE '%{{ ti.xcom_pull(task_ids='download_data', key='year') }}{{ ti.xcom_pull(task_ids='download_data', key='month') | string | rjust(2, '0') }}%';