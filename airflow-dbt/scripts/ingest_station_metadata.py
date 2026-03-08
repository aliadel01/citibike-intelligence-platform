import os
import json
import requests
from azure.storage.blob import BlobServiceClient

def ingest_station_metadata(execution_date, **context):
    # --- Station metadata URL ---
    url = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"

    # --- Azure ADLS Gen2 credentials ---
    storage_account_name = "citibikedatalake"
    container_name = "bronze/station_metadata"
    sas_token = os.getenv("AZURE_SAS_TOKEN")  

    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=sas_token
    )

    container_client = blob_service_client.get_container_client(container_name)

    # Download JSON
    response = requests.get(url)
    data = response.content  # raw bytes of JSON

    # Name of the file to upload
    blob_name = f"station_information_{execution_date}.json"

    # Upload to ADLS Gen2
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(data, overwrite=True)