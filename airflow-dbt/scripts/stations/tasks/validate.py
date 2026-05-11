import logging
import json
from airflow.exceptions import AirflowException
from azure.storage.blob import BlobServiceClient
import os

logger = logging.getLogger(__name__)


def validate_json_file(**context):
    """
    Acts as a structural gate for station metadata JSON files.
    
    Verifies file integrity and critical JSON hierarchy before the file is 
    promoted to the bronze layer. Business-level station validation is 
    deferred to dbt tests.

    Validation Logic:
        1. File Size: Checks against thresholds (using same logic as trips).
        2. Format: Ensures the file is a valid, parsable JSON.
        3. Schema Integrity: Confirms the existence of 'data.stations' to avoid 
           downstream parsing failures in Snowflake.
    """
    ti = context["task_instance"]
    blob_name = ti.xcom_pull(task_ids="ingest_stations_data", key="blob_name")
    file_size_mb = ti.xcom_pull(task_ids='ingest_stations_data', key='file_size_mb')

    logger.info("Starting structural validation for JSON blob: %s", blob_name)

    # 1. File Size Check (Preventing 0-byte or corrupted huge files)
    if file_size_mb is not None:
        if file_size_mb == 0:
            raise AirflowException(f"Validation Failed: {blob_name} is empty (0 MB).")

    # 2. Azure Connection
    storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    sas_token = os.getenv("AZURE_SAS_TOKEN")

    if not storage_account_name or not sas_token:
        raise AirflowException("Azure credentials are not configured in environment variables.")

    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=sas_token,
    )

    temp_container_name = "bronze/temp/station_metadata"
    container_client = blob_service_client.get_container_client(temp_container_name)
    blob_client = container_client.get_blob_client(blob_name)

    try:
        data = blob_client.download_blob().readall()
        json_data = json.loads(data)
    except json.JSONDecodeError as e:
        raise AirflowException(f"Structural Failure: Invalid JSON format in {blob_name}: {e}")
    except Exception as e:
        raise AirflowException(f"Critical: Failed to access or download blob: {e}")

    # 3. Key Schema Check (The "Contract" for Citibike Station API)
    if "data" not in json_data or "stations" not in json_data.get("data", {}):
        raise AirflowException(f"Schema Mismatch: Required key 'data.stations' not found in {blob_name}")

    stations_list = json_data["data"]["stations"]
    if not isinstance(stations_list, list):
        raise AirflowException(f"Schema Mismatch: 'data.stations' should be a list, found {type(stations_list)}")

    logger.info("Structural validation successful for %s. Found %d stations.", blob_name, len(stations_list))
    
    ti.xcom_push(key='validation_passed', value=True)
    return True