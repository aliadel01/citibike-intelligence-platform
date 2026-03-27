import logging
import os
import tempfile
from zipfile import ZipFile

import requests
from airflow.exceptions import AirflowException
from azure.storage.blob import BlobServiceClient

from scripts.utils.get_execution_context import get_execution_context

logger = logging.getLogger(__name__)

HTTP_TIMEOUT = 300
DOWNLOAD_CHUNK_SIZE = 8192


def ingest_tripdata(**context):
    ctx = get_execution_context(**context)
    year = ctx['year']
    month = ctx['month']
    year_month = ctx['year_month']

    url = f"https://s3.amazonaws.com/tripdata/JC-{year_month}-citibike-tripdata.csv.zip"

    storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    container_name = "bronze/trip_data"
    sas_token = os.getenv("AZURE_SAS_TOKEN")

    if not storage_account_name:
        raise AirflowException("AZURE_STORAGE_ACCOUNT_NAME not set.")
    if not sas_token:
        raise AirflowException("AZURE_SAS_TOKEN not set.")

    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=sas_token,
    )
    container_client = blob_service_client.get_container_client(container_name)

    # Stream download to temp file to avoid loading entire ZIP into memory
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=True) as tmp:
        response = requests.get(url, stream=True, timeout=HTTP_TIMEOUT)
        response.raise_for_status()

        total_bytes = 0
        for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
            tmp.write(chunk)
            total_bytes += len(chunk)
        tmp.flush()

        file_size_mb = round(total_bytes / (1024 * 1024), 2)
        logger.info("Downloaded %s (%.2f MB)", url, file_size_mb)

        uploaded_files = []
        with ZipFile(tmp.name) as zf:
            for file_name in zf.namelist():
                data = zf.read(file_name)
                blob_client = container_client.get_blob_client(file_name)
                blob_client.upload_blob(data, overwrite=True)
                uploaded_files.append(file_name)
                logger.info("Uploaded: %s", file_name)

    csv_filename = uploaded_files[0] if uploaded_files else f"JC-{year_month}-citibike-tripdata.csv"

    ti = context['task_instance']
    ti.xcom_push(key='year', value=year)
    ti.xcom_push(key='month', value=month)
    ti.xcom_push(key='csv_filename', value=csv_filename)
    ti.xcom_push(key='file_size_mb', value=file_size_mb)
