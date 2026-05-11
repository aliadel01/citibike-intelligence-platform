import os
import logging
import time
from airflow.exceptions import AirflowException
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)

def move_trips_to_bronze(**context):
    ti = context["task_instance"]
    blob_name = ti.xcom_pull(task_ids="ingest_trips_data", key="csv_filename")

    if not blob_name:
        raise AirflowException("No blob_name found in XCom. Task ingest_tripdata might have failed.")

    storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    sas_token = os.getenv("AZURE_SAS_TOKEN")
    
    blob_service_client = BlobServiceClient(
        f"https://{storage_account_name}.blob.core.windows.net", sas_token
    )

    source_container = "bronze/temp/trip_data"
    dest_container = "bronze/trip_data_validated"

    source_blob = blob_service_client.get_blob_client(source_container, blob_name)
    dest_blob = blob_service_client.get_blob_client(dest_container, blob_name)

    logger.info("Moving %s from temp to validated folder...", blob_name)

    dest_blob.start_copy_from_url(source_blob.url)

    props = dest_blob.get_blob_properties()
    while props.copy.status == 'pending':
        logger.info("Copy status: pending... waiting 2 seconds")
        time.sleep(2)
        props = dest_blob.get_blob_properties()

    if props.copy.status != 'success':
        raise AirflowException(f"Copy failed with status: {props.copy.status}")

    source_blob.delete_blob()
    logger.info("Successfully moved %s and deleted source temp file", blob_name)