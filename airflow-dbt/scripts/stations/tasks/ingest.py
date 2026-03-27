import logging
import os

import requests
from airflow.exceptions import AirflowException
from azure.storage.blob import BlobServiceClient

from scripts.utils.get_execution_context import get_execution_context

logger = logging.getLogger(__name__)

HTTP_TIMEOUT = 300


def ingest_stations_data(**context):
    url = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"
    logger.info("Starting station data ingestion from URL: %s", url)
    
    ctx = get_execution_context(**context)
    execution_date = ctx['execution_date']
    year = ctx['year']
    month = ctx['month']
    logger.info("Execution context retrieved - Date: %s, Year: %s, Month: %s", execution_date, year, month)

    storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    container_name = "bronze/station_metadata"
    sas_token = os.getenv("AZURE_SAS_TOKEN")
    logger.info("Azure credentials loaded - Storage Account: %s, Container: %s", storage_account_name, container_name)

    if not storage_account_name:
        logger.error("AZURE_STORAGE_ACCOUNT_NAME environment variable is not set")
        raise AirflowException("AZURE_STORAGE_ACCOUNT_NAME not set.")
    if not sas_token:
        logger.error("AZURE_SAS_TOKEN environment variable is not set")
        raise AirflowException("AZURE_SAS_TOKEN not set.")
    logger.info("Azure credentials validation passed")

    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=sas_token,
    )
    logger.info("BlobServiceClient initialized successfully")
    
    container_client = blob_service_client.get_container_client(container_name)
    logger.info("Container client created for container: %s", container_name)

    try:
        response = requests.get(url, timeout=HTTP_TIMEOUT)
        response.raise_for_status()
        logger.info("HTTP request successful - Status Code: %s", response.status_code)
    except requests.exceptions.RequestException as e:
        logger.error("Failed to fetch data from URL: %s - Error: %s - Status Code: %s", url, str(e), response.status_code)
        raise
    
    data = response.content
    logger.info("Response data retrieved - Size: %d bytes", len(data))

    blob_name = f"station_information_{execution_date}.json"
    logger.info("Uploading blob: %s", blob_name)
    
    try:
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(data, overwrite=True)
        logger.info("Blob uploaded successfully: %s", blob_name)
    except Exception as e:
        logger.error("Failed to upload blob %s - Error: %s", blob_name, str(e))
        raise

    file_size_mb = round(len(data) / (1024 * 1024), 2)
    logger.info("Uploaded %s (%.2f MB)", blob_name, file_size_mb)

    ti = context['task_instance']
    ti.xcom_push(key='year', value=year)
    ti.xcom_push(key='month', value=month)
    ti.xcom_push(key='blob_name', value=blob_name)
    ti.xcom_push(key='file_size_mb', value=file_size_mb)
    logger.info("XCom values pushed - year: %s, month: %s, blob_name: %s, file_size_mb: %.2f", year, month, blob_name, file_size_mb)
    
    logger.info("Station data ingestion completed successfully")