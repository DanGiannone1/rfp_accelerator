from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
    SearchIndex
)
from datetime import datetime, timezone
import json
import hashlib
from typing import Any

from azure.core.credentials import AzureKeyCredential  
from azure.search.documents import SearchClient  
from datetime import datetime
import os  
from dotenv import load_dotenv  
from azure.core.credentials import AzureKeyCredential  
from azure.identity import DefaultAzureCredential

from openai import AzureOpenAI  
from langchain_openai import AzureChatOpenAI

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient

import uuid
from dotenv import load_dotenv 

load_dotenv()

# Storage settings
storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
container_name = "sales0collateral"

# Azure Document Intelligence settings
form_recognizer_endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
form_recognizer_key = os.getenv("FORM_RECOGNIZER_KEY")

# Azure AI Search settings
ai_search_endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
ai_search_key = os.environ["AZURE_SEARCH_KEY"]
ai_search_index = "sales_collateral"

# Azure OpenAI settings
aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
aoai_key = os.getenv("AZURE_OPENAI_API_KEY")
aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

# Initialize DefaultAzureCredential
credential = DefaultAzureCredential()

# Initialize blob service client with DefaultAzureCredential
blob_service_client = BlobServiceClient(
    account_url=f"https://{storage_account_name}.blob.core.windows.net",
    credential=credential
)

# Initialize other clients
document_intelligence_client = DocumentIntelligenceClient(
    form_recognizer_endpoint, 
    AzureKeyCredential(form_recognizer_key)
)

search_index_client = SearchIndexClient(
    ai_search_endpoint, 
    AzureKeyCredential(ai_search_key)
)

search_client = SearchClient(
    ai_search_endpoint, 
    ai_search_index, 
    AzureKeyCredential(ai_search_key)
)

aoai_client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
    api_key=os.getenv("AZURE_OPENAI_KEY"),  
    api_version="2023-05-15"
)

def generate_embeddings(text, model="text-embedding-ada-002"):
    return aoai_client.embeddings.create(input=[text], model=model).data[0].embedding

def read_pdf(input_file):
    # Generate SAS token for Document Intelligence to access the blob
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(input_file)
    
    # Use the blob URL directly since we're using DefaultAzureCredential
    blob_url = blob_client.url
    
    analyze_request = {
        "urlSource": blob_url
    }
    poller = document_intelligence_client.begin_analyze_document("prebuilt-layout", analyze_request=analyze_request)
    result: AnalyzeResult = poller.result()
    
    return result.content

def create_index():
    try:
        search_index_client.get_index(ai_search_index)
        print("Index already exists")
        return
    except:
        pass

    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SimpleField(name="date", type=SearchFieldDataType.DateTimeOffset, filterable=True, facetable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchableField(name="sourceFileName", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="sourceFilePage", type=SearchFieldDataType.Int32, filterable=True),
        SearchField(
            name="searchVector", 
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True, 
            vector_search_dimensions=1536, 
            vector_search_profile_name="myHnswProfile"
        )
    ]

    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
            )
        ]
    )

    index = SearchIndex(
        name=ai_search_index, 
        fields=fields,
        vector_search=vector_search
    )
    
    result = search_index_client.create_or_update_index(index)
    print("Index has been created")

def generate_document_id(blob_name):
    """Generate a unique, deterministic ID for a document."""
    unique_string = f"{blob_name}"
    return hashlib.md5(unique_string.encode()).hexdigest()

def list_blobs_in_folder(container_client, folder_name):
    return [blob for blob in container_client.list_blobs() if blob.name.startswith(folder_name)]

def move_blob(container_client, source_blob_name, destination_blob_name):
    source_blob = container_client.get_blob_client(source_blob_name)
    destination_blob = container_client.get_blob_client(destination_blob_name)
    
    destination_blob.start_copy_from_url(source_blob.url)
    source_blob.delete_blob()

def populate_index():
    print("Populating index...")
    container_client = blob_service_client.get_container_client(container_name)
    
    stage_blobs = list_blobs_in_folder(container_client, "source/")
    print(f"Found {len(stage_blobs)} blobs in the 'source' folder")
    
    for blob in stage_blobs:
        print(f"Processing {blob.name}")
        
        try:
            full_text = read_pdf(blob.name)
            searchVector = generate_embeddings(full_text)
            current_date = datetime.now(timezone.utc).isoformat()
            document_id = generate_document_id(blob.name)
            fileName = os.path.basename(blob.name)
            
            # For simplicity, setting page number to 1
            # You might want to modify this based on your actual PDF parsing logic
            page_number = 1
            
            document = {
                "id": document_id,
                "date": current_date,
                "content": full_text,
                "sourceFileName": fileName,
                "sourceFilePage": page_number,
                "searchVector": searchVector
            }
            
            search_client.upload_documents(documents=[document])
            
            # Move the processed file to the 'processed' folder
            destination_blob_name = blob.name.replace("source/", "processed/")
            move_blob(container_client, blob.name, destination_blob_name)
            
            print(f"Successfully processed and moved {blob.name}")
        
        except Exception as e:
            print(f"Error processing {blob.name}: {str(e)}")

def reset_processed_files():
    """Move all files from the 'processed' folder back to the 'source' folder."""
    container_client = blob_service_client.get_container_client(container_name)
    
    processed_blobs = list_blobs_in_folder(container_client, "processed/")
    
    for blob in processed_blobs:
        source_blob_name = blob.name
        destination_blob_name = source_blob_name.replace("processed/", "source/")
        
        try:
            move_blob(container_client, source_blob_name, destination_blob_name)
        except Exception as e:
            print(f"Error moving {source_blob_name} back to 'source': {str(e)}")

if __name__ == "__main__":
    create_index()
    populate_index()