import os
import requests
from io import BytesIO
from zipfile import ZipFile
from azure.storage.blob import BlobServiceClient

def ingest_tripdata(execution_date, **context):
    # --- S3 file ---
    year_month = f"JC-{execution_date.strftime('%Y%m')}"

    # -------------------------------
    # Config
    # -------------------------------
    url = f"https://s3.amazonaws.com/tripdata/{year_month}-citibike-tripdata.csv.zip"

    storage_account_name = "citibikedatalake"
    container_name = "trip-data"
    sas_token = os.getenv("AZURE_SAS_TRIP_TOKEN")  

    if not sas_token:
        raise ValueError("SAS token not found. Set AZURE_SAS_TRIP_TOKEN in your environment.")

    # -------------------------------
    # Connect to Azure Blob
    # -------------------------------
    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=sas_token
    )

    container_client = blob_service_client.get_container_client(container_name)

    # -------------------------------
    # Download S3 ZIP
    # -------------------------------
    response = requests.get(url)
    response.raise_for_status()  # Ensure URL is valid

    with ZipFile(BytesIO(response.content)) as zipfile:
        for file_name in zipfile.namelist():
            data = zipfile.read(file_name)
            blob_client = container_client.get_blob_client(file_name)
            blob_client.upload_blob(data, overwrite=True)
            print(f"Uploaded: {file_name}")