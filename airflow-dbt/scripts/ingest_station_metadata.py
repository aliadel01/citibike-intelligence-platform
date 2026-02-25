url = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"

import os
import requests
from io import BytesIO
from zipfile import ZipFile
from azure.storage.blob import BlobServiceClient

def ingest_station_metadata(execution_date, **context):
    # --- Station metadata URL ---
    url = "https://gbfs.citibikenyc.com/gbfs/en/station_information.json"

    # --- Azure ADLS Gen2 credentials ---
    storage_account_name = "citibikedatalake"
    container_name = "station-metadata"
    sas_token = os.getenv("AZURE_SAS_STATION_TOKEN")  

    blob_service_client = BlobServiceClient(
        account_url=f"https://{storage_account_name}.blob.core.windows.net",
        credential=sas_token
    )

    container_client = blob_service_client.get_container_client(container_name)

    # Download S3 ZIP
    response = requests.get(url)
    zipfile = ZipFile(BytesIO(response.content))

    # Upload each file in ZIP to ADLS
    for file_name in zipfile.namelist():
        data = zipfile.read(file_name)
        blob_client = container_client.get_blob_client(file_name)
        blob_client.upload_blob(data, overwrite=True)