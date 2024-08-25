import os
from dotenv import load_dotenv


import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey


# Azure Cosmos DB





def get_rfp_analysis_from_db(rfp_name):
    if not rfp_name:
        return "RFP name is required"

    COSMOS_HOST = os.getenv("COSMOS_HOST")
    COSMOS_MASTER_KEY = os.getenv("COSMOS_MASTER_KEY")
    COSMOS_DATABASE_ID = os.getenv("COSMOS_DATABASE_ID")
    COSMOS_CONTAINER_ID = os.getenv("COSMOS_CONTAINER_ID")

    client = cosmos_client.CosmosClient(COSMOS_HOST, {'masterKey': COSMOS_MASTER_KEY}, user_agent="CosmosDBAgent", user_agent_overwrite=True)
    try:
        try:
            db = client.create_database(id=COSMOS_DATABASE_ID)
            print('Database with id \'{0}\' created'.format(COSMOS_DATABASE_ID))
        except exceptions.CosmosResourceExistsError:
            db = client.get_database_client(COSMOS_DATABASE_ID)
            print('Database with id \'{0}\' was found'.format(COSMOS_DATABASE_ID))

        try:
            container = db.create_container(id=COSMOS_CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
            print('Container with id \'{0}\' created'.format(COSMOS_CONTAINER_ID))
        except exceptions.CosmosResourceExistsError:
            container = db.get_container_client(COSMOS_CONTAINER_ID)
            print('Container with id \'{0}\' was found'.format(COSMOS_CONTAINER_ID))
    except exceptions.CosmosHttpResponseError as e:
        print('\nrun_sample has caught an error. {0}'.format(e.message))
        return "An error occurred while connecting to CosmosDB"

    try:
        query = f"SELECT c.skills_and_experience FROM c WHERE c.partitionKey = '{rfp_name}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        if items:
            return items[0]['skills_and_experience']
        else:
            return "RFP analysis not found"
    except Exception as e:
        print(f"Error querying CosmosDB: {str(e)}")
        return "An error occurred while fetching RFP analysis"
