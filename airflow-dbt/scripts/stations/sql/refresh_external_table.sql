-- Refresh external table metadata
ALTER EXTERNAL TABLE CITIBIKE_DB.EXTERNAL.v_station_metadata REFRESH;

-- Verify row count
SELECT COUNT(*) AS row_count 
FROM CITIBIKE_DB.EXTERNAL.v_station_metadata
WHERE source_file LIKE '%{{ ti.xcom_pull(task_ids='ingest_stations_data', key='year') }}{{ ti.xcom_pull(task_ids='ingest_stations_data', key='month') | string | rjust(2, '0') }}%';