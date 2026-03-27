-- Log successful ingestion
INSERT INTO CITIBIKE_DB.EXTERNAL.INGESTION_LOG (
    ingestion_date,
    year,
    month,
    source_file,
    row_count,
    file_size_mb,
    status,
    created_at
)
VALUES (
    '{{ ds }}',
    {{ ti.xcom_pull(task_ids='ingest_trips_data', key='year') }},
    {{ ti.xcom_pull(task_ids='ingest_trips_data', key='month') }},
    '{{ ti.xcom_pull(task_ids='ingest_trips_data', key='csv_filename') }}',
    {{ ti.xcom_pull(task_ids='validate_data', key='row_count') }},
    {{ ti.xcom_pull(task_ids='ingest_trips_data', key='file_size_mb') }},
    'SUCCESS',
    CURRENT_TIMESTAMP()
);
