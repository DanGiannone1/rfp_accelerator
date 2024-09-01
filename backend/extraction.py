import os
from dotenv import load_dotenv
import threading
import time
from azure.cosmos import CosmosClient
from langchain_openai import AzureChatOpenAI
import json
from prompts import content_parsing_prompt


load_dotenv()

# Azure Cosmos DB configuration
COSMOS_HOST = os.getenv("COSMOS_HOST")
COSMOS_MASTER_KEY = os.getenv("COSMOS_MASTER_KEY")
COSMOS_DATABASE_ID = os.getenv("COSMOS_DATABASE_ID")
COSMOS_CONTAINER_ID = os.getenv("COSMOS_CONTAINER_ID")

# Azure OpenAI configuration
aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
aoai_key = os.getenv("AZURE_OPENAI_API_KEY")
aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")

# Initialize Cosmos DB client
cosmos_client = CosmosClient(COSMOS_HOST, credential=COSMOS_MASTER_KEY)
database = cosmos_client.get_database_client(COSMOS_DATABASE_ID)
container = database.get_container_client(COSMOS_CONTAINER_ID)

# Initialize Azure OpenAI client
primary_llm = AzureChatOpenAI(
    azure_deployment=aoai_deployment,
    api_version="2024-05-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=aoai_key,
    azure_endpoint=aoai_endpoint
)

primary_llm_json = AzureChatOpenAI(
    azure_deployment=aoai_deployment,
    api_version="2024-05-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=aoai_key,
    azure_endpoint=aoai_endpoint,
    model_kwargs={"response_format": {"type": "json_object"}}
)




def extract_requirements(section_content):
    messages = [
        {"role": "system", "content": content_parsing_prompt},
        {"role": "user", "content": section_content}
    ]
    response = primary_llm_json.invoke(messages)
    response_json = json.loads(response.content)
    
    # Access the analysis and output fields
    analysis = response_json.get('analysis')
    output = response_json.get('output')
    print("Analysis:", analysis)
    print("Output:", output)

    return response_json

def extraction_process(rfp_name):
    query = f"SELECT * FROM c WHERE c.partitionKey = '{rfp_name}' AND IS_DEFINED(c.section_content)"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    
    total_items = len(items)
    processed_items = 0
    
    for item in items:
        section_content = item['section_content']
        requirements_json = extract_requirements(section_content)
        
        # Update the item in Cosmos DB
        item['requirements'] = requirements_json
        container.upsert_item(item)
        
        processed_items += 1
        progress = (processed_items / total_items) * 100
        print(f"Extraction progress: {progress:.2f}%")

def start_extraction_thread(rfp_name):
    thread = threading.Thread(target=extraction_process, args=(rfp_name,))
    thread.start()

# Function to get extraction progress
def get_extraction_progress(rfp_name):
    query = f"SELECT VALUE COUNT(1) FROM c WHERE c.partitionKey = '{rfp_name}' AND IS_DEFINED(c.requirements)"
    result = list(container.query_items(query=query, enable_cross_partition_query=True))
    processed_count = result[0] if result else 0
    
    query = f"SELECT VALUE COUNT(1) FROM c WHERE c.partitionKey = '{rfp_name}' AND IS_DEFINED(c.section_content)"
    result = list(container.query_items(query=query, enable_cross_partition_query=True))
    total_count = result[0] if result else 0
    
    if total_count == 0:
        return 0
    
    return (processed_count / total_count) * 100