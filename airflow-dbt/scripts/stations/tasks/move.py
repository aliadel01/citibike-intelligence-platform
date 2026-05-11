import logging
import os
from airflow.exceptions import AirflowException
from azure.storage.blob import BlobServiceClient

logger = logging.getLogger(__name__)

def cleanup_old_station_files(container_client, folder_path):
    
    blobs_to_delete = container_client.list_blobs(name_starts_with=folder_path)
    
    for blob in blobs_to_delete:
        container_client.delete_blob(blob.name)
        logger.info(f"Deleted old station file: {blob.name}")

def move_to_bronze_and_cleanup(**context):
    ti = context["task_instance"]
    blob_name = ti.xcom_pull(task_ids="ingest_stations_data", key="blob_name")

    logger.info("Starting move operation for blob: %s", blob_name)

    storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    sas_token = os.getenv("AZURE_SAS_TOKEN")

    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=sas_token,
    )

    container_name = "bronze"
    container_client = blob_service_client.get_container_client(container_name)

    temp_folder = "temp/station_metadata/"
    validated_folder = "station_metadata_validated/"

    try:
        logger.info("Cleaning up old files in %s", validated_folder)
        cleanup_old_station_files(container_client, validated_folder)

        source_blob_path = f"{temp_folder}{blob_name}"
        source_blob_client = container_client.get_blob_client(source_blob_path)
        data = source_blob_client.download_blob().readall()
        logger.info("Downloaded from temp: %s", source_blob_path)

        target_blob_path = f"{validated_folder}{blob_name}"
        target_blob_client = container_client.get_blob_client(target_blob_path)
        target_blob_client.upload_blob(data, overwrite=True)
        logger.info("Uploaded to bronze: %s", target_blob_path)

        source_blob_client.delete_blob()
        logger.info("Deleted source temp blob")

        logger.info("Move and cleanup operation completed successfully.")

    except Exception as e:
        logger.error("Failed to move blob: %s", str(e))
        raise AirflowException(f"Operation failed: {str(e)}")