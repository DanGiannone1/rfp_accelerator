"""
### adls.py ###

This module handles interactions with Azure Data Lake Storage Gen2 (which is built on Azure Blob Storage).
It provides functionality to upload files, list blobs, and move blobs between containers. The goal of this module is to provide 
clear and concise examples of how to run basic ADLS operations using a particular SDK version. 

Requirements:
    azure-storage-blob==12.22.0
    python-dotenv
"""

import os
import logging
from typing import Union, Dict, Any, List
from dotenv import load_dotenv
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import io

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Set to WARNING to suppress INFO logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set our logger to INFO

# Disable other loggers
logging.getLogger('azure').setLevel(logging.WARNING)
logging.getLogger('azure.storage').setLevel(logging.WARNING)
logging.getLogger('azure.identity').setLevel(logging.WARNING)

class ADLSManager:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        """Control instance creation to ensure only one instance exists."""
        if cls._instance is None:
            logger.info("Creating new ADLSManager instance")
            cls._instance = super(ADLSManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the ADLS client if not already initialized."""
        if not self._is_initialized:
            logger.info("Initializing ADLSManager")
            self._load_env_variables()
            self.blob_service_client = self._get_blob_service_client()
            ADLSManager._is_initialized = True

    def _load_env_variables(self):
        load_dotenv()
        self.storage_account_name = os.environ.get("STORAGE_ACCOUNT_NAME")
        self.storage_account_key = os.environ.get("STORAGE_ACCOUNT_KEY")
        self.storage_account_container = os.environ.get("STORAGE_ACCOUNT_CONTAINER", "documents")
        self.tenant_id = os.environ.get("TENANT_ID", '16b3c013-d300-468d-ac64-7eda0820b6d3')

        if not self.storage_account_name:
            raise ValueError("STORAGE_ACCOUNT_NAME environment variable is not set")

    def _get_blob_service_client(self) -> BlobServiceClient:
        logger.info("Initializing Blob service client")
        if self.storage_account_key:
            logger.info("Using key-based authentication for Blob storage")
            connection_string = f"DefaultEndpointsProtocol=https;AccountName={self.storage_account_name};AccountKey={self.storage_account_key};EndpointSuffix=core.windows.net"
            return BlobServiceClient.from_connection_string(connection_string)
        else:
            logger.info("Using DefaultAzureCredential for Blob storage authentication")
            account_url = f"https://{self.storage_account_name}.blob.core.windows.net"
            credential = DefaultAzureCredential(
                interactive_browser_tenant_id=self.tenant_id,
                visual_studio_code_tenant_id=self.tenant_id,
                workload_identity_tenant_id=self.tenant_id,
                shared_cache_tenant_id=self.tenant_id
            )
            return BlobServiceClient(account_url=account_url, credential=credential)

    def upload_to_blob(self, file_content: Union[bytes, io.IOBase], filename: str, container_name: str = None) -> Dict[str, str]:
        container_name = container_name or self.storage_account_container
        container_client = self.blob_service_client.get_container_client(container_name)
        blob_client = container_client.get_blob_client(filename)
        
        if isinstance(file_content, io.IOBase):
            blob_client.upload_blob(file_content.read(), overwrite=True)
        else:
            blob_client.upload_blob(file_content, overwrite=True)
        
        logger.info(f"File {filename} uploaded successfully")
        return {"message": f"File {filename} uploaded successfully", "blob_url": blob_client.url}

    def list_blobs_in_folder(self, folder_name: str, container_name: str = None) -> List[Any]:
        container_name = container_name or self.storage_account_container
        container_client = self.blob_service_client.get_container_client(container_name)
        
        return [blob for blob in container_client.list_blobs() if blob.name.startswith(folder_name)]

    def move_blob(self, source_blob_name: str, 
                  destination_blob_name: str, 
                  source_container_name: str = None, 
                  destination_container_name: str = None) -> Dict[str, str]:
        source_container_name = source_container_name or self.storage_account_container
        destination_container_name = destination_container_name or source_container_name

        source_container_client = self.blob_service_client.get_container_client(source_container_name)
        destination_container_client = self.blob_service_client.get_container_client(destination_container_name)

        source_blob = source_container_client.get_blob_client(source_blob_name)
        destination_blob = destination_container_client.get_blob_client(destination_blob_name)
        
        destination_blob.start_copy_from_url(source_blob.url)
        source_blob.delete_blob()
        message = f"Moved blob from {source_blob_name} to {destination_blob_name}"
        logger.info(message)
        return {"message": message}

def run_examples():
    try:
        # Create an instance - will reuse the same instance if already created
        adls_manager = ADLSManager()
        
        # Local file upload scenario
        sample_file_path = "your/file/path/sample.pdf"
        logger.info("Uploading local file...")
        with open(sample_file_path, 'rb') as file:
            upload_result = adls_manager.upload_to_blob(file, os.path.basename(sample_file_path))
        logger.info(f"Local file upload: {upload_result['message']}")
        
        # Bytestream upload scenario
        logger.info("Uploading file as bytestream...")
        with open(sample_file_path, 'rb') as file:
            file_content = file.read()
        upload_result = adls_manager.upload_to_blob(file_content, "bytestream_" + os.path.basename(sample_file_path))
        logger.info(f"Bytestream upload: {upload_result['message']}")
        
        # Example of listing blobs in a folder
        logger.info("Listing blobs in 'source' folder...")
        blobs = adls_manager.list_blobs_in_folder("source/")
        logger.info(f"Found {len(blobs)} blobs in the 'source' folder")

        # Example of moving a blob
        if blobs:
            source_blob_name = blobs[0].name
            destination_blob_name = source_blob_name.replace("source/", "processed/")
            logger.info(f"Moving blob {source_blob_name} to {destination_blob_name}...")
            move_result = adls_manager.move_blob(source_blob_name, destination_blob_name)
            logger.info(move_result['message'])

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    run_examples()