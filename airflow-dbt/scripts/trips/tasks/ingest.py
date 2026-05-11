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


def ingest_tripdata_to_temp(**context):
    # Retrieve execution context (year, month, etc.)
    ctx = get_execution_context(**context)
    year_month = ctx['year_month']
    
    # Construct the source URL for the Citibike zip file
    url = f"https://s3.amazonaws.com/tripdata/JC-{year_month}-citibike-tripdata.csv.zip"

    # Load Azure Storage credentials from environment variables
    storage_account_name = os.getenv("AZURE_STORAGE_ACCOUNT_NAME")
    temp_container_name = "bronze/temp/trip_data"
    sas_token = os.getenv("AZURE_SAS_TOKEN")

    # Initialize the Azure Blob Service Client
    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=sas_token,
    )
    # Get the client for the specific temporary container
    container_client = blob_service_client.get_container_client(temp_container_name)

    # Create a named temporary file that will be auto-deleted after the 'with' block
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=True) as tmp:
        # Stream the download from the URL to handle large files efficiently
        response = requests.get(url, stream=True, timeout=HTTP_TIMEOUT)
        response.raise_for_status()

        # Write the downloaded chunks into the temporary file
        total_bytes = 0
        for chunk in response.iter_content(chunk_size=DOWNLOAD_CHUNK_SIZE):
            tmp.write(chunk)
            total_bytes += len(chunk)
        
        # Ensure all data is written to the disk
        tmp.flush()

        # CRITICAL: Calculate file size while the temporary file still exists
        file_size_mb = round(total_bytes / (1024 * 1024), 2)
        logger.info("Downloaded %s (%.2f MB)", url, file_size_mb)

        uploaded_files = []
        # Open the downloaded zip file to extract and upload its content
        with ZipFile(tmp.name) as zf:
            for file_name in zf.namelist():
                # Read the file content from the zip
                data = zf.read(file_name)
                # Get a blob client for the extracted file
                blob_client = container_client.get_blob_client(file_name)
                # Upload the extracted data directly to Azure Blob Storage
                blob_client.upload_blob(data, overwrite=True)
                uploaded_files.append(file_name)
                logger.info("Uploaded: %s", file_name)

    # After exiting the 'with' block, the local tmp file is deleted automatically
    # Get the name of the first uploaded CSV file
    csv_filename = uploaded_files[0] if uploaded_files else f"JC-{year_month}-citibike-tripdata.csv"
    
    # Push metadata to XCom for use in downstream tasks (Validation/Move)
    ti = context['task_instance']
    ti.xcom_push(key='csv_filename', value=csv_filename)
    ti.xcom_push(key='file_size_mb', value=file_size_mb)
    ti.xcom_push(key='year', value=ctx['year'])
    ti.xcom_push(key='month', value=ctx['month'])
    
    return True