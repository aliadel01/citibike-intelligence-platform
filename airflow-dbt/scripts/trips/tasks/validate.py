import logging
import os
import io
import pandas as pd
from airflow.exceptions import AirflowException
from azure.storage.blob import BlobServiceClient

from scripts.utils.config import (
    MIN_FILE_SIZE_MB,
    MAX_FILE_SIZE_MB,
)

logger = logging.getLogger(__name__)

def validate_tripdata_in_temp(**context):
    """
    Acts as a lightweight structural gate for ingested CSV files.
    
    Validates the physical properties and schema of the file before it is 
    registered in the Snowflake Bronze layer. Detailed data quality (nulls, logic) 
    is deferred to downstream dbt tests.

    Validation Logic:
        1. File Size: Validates against MIN/MAX thresholds to catch empty/bloated files.
        2. Connectivity: Ensures the Azure Blob is reachable.
        3. Schema Integrity: Confirms all 2021+ required columns exist to avoid Snowflake COPY errors.
    """
    ti = context['task_instance']
    blob_name = ti.xcom_pull(task_ids='ingest_trips_data', key='csv_filename')
    file_size_mb = ti.xcom_pull(task_ids='ingest_trips_data', key='file_size_mb')

    logger.info("Starting validation for blob: %s", blob_name)

    storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    sas_token = os.getenv("AZURE_SAS_TOKEN")
    
    if not storage_account_name or not sas_token:
        raise AirflowException("Azure credentials are not set in environment variables.")

    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=sas_token,
    )
    
    temp_container_name = "bronze/temp/trip_data"
    container_client = blob_service_client.get_container_client(temp_container_name)
    blob_client = container_client.get_blob_client(blob_name)

    # --- Check 1: File size ---
    if file_size_mb < MIN_FILE_SIZE_MB or file_size_mb > MAX_FILE_SIZE_MB:
        message = f"File size validation failed: {file_size_mb} MB"
        logger.error(message)
        raise AirflowException(message)

    try:
        download_stream = blob_client.download_blob()
        df_sample = pd.read_csv(io.BytesIO(download_stream.readall()), nrows=5000)
        logger.info("Sample of 5000 rows downloaded for validation")
    except Exception as e:
        logger.error("Failed to read CSV from Azure: %s", str(e))
        raise AirflowException(f"Error accessing blob: {e}")

    # --- Check 2: Required columns ---
    required_columns = [
        'ride_id', 'rideable_type', 'started_at', 'ended_at',
        'start_station_name', 'start_station_id',
        'end_station_name', 'end_station_id',
        'member_casual',
    ]
    missing_columns = set(required_columns) - set(df_sample.columns)
    if missing_columns:
        raise AirflowException(f"Missing required columns: {missing_columns}")

    # --- Check 3: Row count ---
    row_count = len(df_sample)
    logger.info("Validation passed for sample of %d rows", row_count)

    logger.info("Validation successful for %s", blob_name)
    
    ti.xcom_push(key='validation_passed', value=True)
    return True