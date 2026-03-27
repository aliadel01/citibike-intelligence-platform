import logging

import pandas as pd
from airflow.exceptions import AirflowException

from scripts.utils.config import (
    MIN_ROWS_PER_MONTH,
    MAX_ROWS_PER_MONTH,
    MIN_FILE_SIZE_MB,
    MAX_FILE_SIZE_MB,
)

logger = logging.getLogger(__name__)


def validate_csv_file(**context):
    """
    Validate downloaded CSV file
    - Check file size
    - Check required columns
    - Check row count
    - Check data types
    """
    ti = context['task_instance']
    csv_path = ti.xcom_pull(task_ids='ingest_trips_data', key='csv_filename')
    file_size_mb = ti.xcom_pull(task_ids='ingest_trips_data', key='file_size_mb')

    logger.info("Validating: %s", csv_path)

    # Check 1: File size
    if file_size_mb < MIN_FILE_SIZE_MB:
        raise AirflowException(
            f"File too small: {file_size_mb:.2f} MB (min: {MIN_FILE_SIZE_MB} MB)"
        )
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise AirflowException(
            f"File too large: {file_size_mb:.2f} MB (max: {MAX_FILE_SIZE_MB} MB)"
        )

    # Check 2: Read sample and check schema
    df_sample = pd.read_csv(csv_path, nrows=1000)

    # Required columns (new schema 2021+)
    required_columns = [
        'ride_id', 'rideable_type', 'started_at', 'ended_at',
        'start_station_name', 'start_station_id',
        'end_station_name', 'end_station_id',
        'member_casual',
    ]

    missing_columns = set(required_columns) - set(df_sample.columns)
    if missing_columns:
        raise AirflowException(f"Missing required columns: {missing_columns}")

    # Check 3: Row count (full file)
    row_count = sum(1 for _ in open(csv_path)) - 1  # Subtract header
    logger.info("Total rows: %s", f"{row_count:,}")

    if row_count < MIN_ROWS_PER_MONTH:
        raise AirflowException(
            f"Too few rows: {row_count:,} (min: {MIN_ROWS_PER_MONTH:,})"
        )
    if row_count > MAX_ROWS_PER_MONTH:
        raise AirflowException(
            f"Too many rows: {row_count:,} (max: {MAX_ROWS_PER_MONTH:,})"
        )

    # Check 4: Data quality on sample
    nulls = df_sample[required_columns].isnull().sum()
    null_pct = (nulls / len(df_sample) * 100).round(2)

    logger.info("Null percentages:\n%s", null_pct)

    # Critical columns shouldn't have > 5% nulls
    critical_nulls = null_pct[null_pct > 5]
    if not critical_nulls.empty:
        raise AirflowException(
            f"High null percentage in critical columns:\n{critical_nulls}"
        )

    # Check 5: Date range validation
    df_sample['started_at'] = pd.to_datetime(df_sample['started_at'])
    df_sample['ended_at'] = pd.to_datetime(df_sample['ended_at'])

    # Check for future dates
    future_dates = (df_sample['started_at'] > pd.Timestamp.now()).sum()
    if future_dates > 0:
        logger.warning("Found %d trips with future dates", future_dates)

    # Check for negative durations
    negative_durations = (df_sample['started_at'] >= df_sample['ended_at']).sum()
    if negative_durations > len(df_sample) * 0.01:  # > 1%
        raise AirflowException(
            f"Too many trips with negative duration: {negative_durations}"
        )

    logger.info("Validation passed")

    ti.xcom_push(key='row_count', value=row_count)
    ti.xcom_push(key='validation_passed', value=True)

    return True
