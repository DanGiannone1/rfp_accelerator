"""
This module handles interactions with Azure Cosmos DB, including database and container creation,
and CRUD operations on documents. It automatically selects between key-based and DefaultAzureCredential
authentication based on the presence of COSMOS_MASTER_KEY. Logging is configured to show only
custom messages.

Requirements:
    azure-cosmos==4.5.1
    azure-identity==1.12.0
"""

import os
import logging
from functools import wraps
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from azure.cosmos import CosmosClient, exceptions, PartitionKey
from azure.cosmos.container import ContainerProxy
from azure.cosmos.database import DatabaseProxy
from azure.identity import DefaultAzureCredential

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.WARNING)  # Set to WARNING to suppress INFO logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Set our logger to INFO

# Disable other loggers
logging.getLogger('azure').setLevel(logging.WARNING)
logging.getLogger('azure.cosmos').setLevel(logging.WARNING)
logging.getLogger('azure.identity').setLevel(logging.WARNING)

# Cosmos DB Configuration
COSMOS_HOST = os.environ.get("COSMOS_HOST")
COSMOS_MASTER_KEY = os.environ.get("COSMOS_MASTER_KEY")
COSMOS_DATABASE_ID = os.environ.get("COSMOS_DATABASE_ID")
COSMOS_CONTAINER_ID = os.environ.get("COSMOS_CONTAINER_ID")

# Azure AD Tenant ID
TENANT_ID = '16b3c013-d300-468d-ac64-7eda0820b6d3'

def cosmos_error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f"Cosmos DB error in {func.__name__}: {e.message}")
            raise
    return wrapper

class CosmosDBManager:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        """Control instance creation to ensure only one instance exists."""
        if cls._instance is None:
            logger.info("Creating new CosmosDBManager instance")
            cls._instance = super(CosmosDBManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the CosmosDB client and create database and container if they don't exist.
        Automatically selects between key-based and DefaultAzureCredential authentication
        based on the presence of COSMOS_MASTER_KEY.

        Raises
        ------
        ValueError
            If any of the required Cosmos DB configuration values are missing.
        """
        if not self._is_initialized:
            logger.info("Initializing CosmosDBManager")
            if not all([COSMOS_HOST, COSMOS_DATABASE_ID, COSMOS_CONTAINER_ID]):
                raise ValueError("Cosmos DB configuration is incomplete")

            if COSMOS_MASTER_KEY:
                logger.info("Using key-based authentication for Cosmos DB")
                self.client: CosmosClient = CosmosClient(COSMOS_HOST, {'masterKey': COSMOS_MASTER_KEY})
            else:
                logger.info("Using DefaultAzureCredential for Cosmos DB authentication")
                credential = DefaultAzureCredential(
                    interactive_browser_tenant_id=TENANT_ID,
                    visual_studio_code_tenant_id=TENANT_ID,
                    workload_identity_tenant_id=TENANT_ID,
                    shared_cache_tenant_id=TENANT_ID
                )
                self.client: CosmosClient = CosmosClient(COSMOS_HOST, credential=credential)

            self.database: Optional[DatabaseProxy] = None
            self.container: Optional[ContainerProxy] = None

            self._initialize_database_and_container()
            CosmosDBManager._is_initialized = True

    def _initialize_database_and_container(self) -> None:
        """
        Create database and container if they don't exist.

        Raises
        ------
        exceptions.CosmosHttpResponseError
            If there's an error in creating or getting the database or container.
        """
        try:
            try:
                self.database = self.client.create_database(id=COSMOS_DATABASE_ID)
                logger.info(f'Database with id \'{COSMOS_DATABASE_ID}\' created')
            except exceptions.CosmosResourceExistsError:
                self.database = self.client.get_database_client(COSMOS_DATABASE_ID)
                logger.info(f'Database with id \'{COSMOS_DATABASE_ID}\' was found')

            try:
                self.container = self.database.create_container(id=COSMOS_CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
                logger.info(f'Container with id \'{COSMOS_CONTAINER_ID}\' created')
            except exceptions.CosmosResourceExistsError:
                self.container = self.database.get_container_client(COSMOS_CONTAINER_ID)
                logger.info(f'Container with id \'{COSMOS_CONTAINER_ID}\' was found')
        except exceptions.CosmosHttpResponseError as e:
            logger.error(f'An error occurred: {e.message}')
            raise

    @cosmos_error_handler
    def create_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item in the container."""
        created_item = self.container.create_item(body=item)
        logger.info(f"Item created with id: {created_item['id']}")
        return created_item

    @cosmos_error_handler
    def read_item(self, item_id: str, partition_key: str) -> Dict[str, Any]:
        """Read an item from the container."""
        item = self.container.read_item(item=item_id, partition_key=partition_key)
        logger.info(f"Item read with id: {item['id']}")
        return item

    @cosmos_error_handler
    def update_item(self, item_id: str, updates: Dict[str, Any], partition_key: str) -> Dict[str, Any]:
        """Update an item in the container."""
        item = self.read_item(item_id, partition_key)
        item.update(updates)
        updated_item = self.container.upsert_item(body=item)
        logger.info(f"Item updated with id: {updated_item['id']}")
        return updated_item

    @cosmos_error_handler
    def delete_item(self, item_id: str, partition_key: str) -> None:
        """Delete an item from the container."""
        self.container.delete_item(item=item_id, partition_key=partition_key)
        logger.info(f"Item deleted with id: {item_id}")

    @cosmos_error_handler
    def query_items(self, query: str, parameters: Optional[List[Dict[str, Any]]] = None, partition_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query items from the container."""
        items = list(self.container.query_items(
            query=query,
            parameters=parameters,
            partition_key=partition_key,
            enable_cross_partition_query=(partition_key is None)
        ))
        logger.info(f"Query returned {len(items)} items")
        return items

    def get_items_by_partition_key(self, partition_key: str) -> List[Dict[str, Any]]:
        """Retrieve all items for a specific partition key."""
        query = "SELECT * FROM c WHERE c.partitionKey = @partitionKey"
        parameters = [{"name": "@partitionKey", "value": partition_key}]
        return self.query_items(query, parameters, partition_key)



def run_examples():
    """Example usage of the CosmosDB class."""
    try:

        cosmos_db = CosmosDBManager()

        logger.info("Connected to Cosmos DB")

        # Create an item
        new_item = {
            'id': 'item1',
            'partitionKey': 'example_partition',
            'name': 'John Doe',
            'age': 30
        }
        created_item = cosmos_db.create_item(new_item)

        # Read the item
        read_item = cosmos_db.read_item('item1', 'example_partition')

        # Update the item
        updated_item = cosmos_db.update_item('item1', {'age': 31}, 'example_partition')

        # Query items
        items = cosmos_db.get_items_by_partition_key('example_partition')

        # Delete the item
        cosmos_db.delete_item('item1', 'example_partition')

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    run_examples()