"""
Upload and processing module for RFP documents.

This module handles the uploading of RFP documents to Azure Blob Storage,
processing them using Azure Document Intelligence, and analyzing the content
using Azure OpenAI. It also manages writing the analysis results to Azure Cosmos DB.

This module calls "chunking.py" to chunk the RFP into sections. 

"""

# Standard library imports
import json
import os
import time
from io import BytesIO

# Third-party imports
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import AnalyzeResult
from azure.core.credentials import AzureKeyCredential
from azure.cosmos.partition_key import PartitionKey
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Local imports
from chunking import start_chunking_process
from prompts import overview_prompt

# Load environment variables
load_dotenv()

# Azure Form Recognizer configuration
FORM_RECOGNIZER_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")
FORM_RECOGNIZER_KEY = os.getenv("FORM_RECOGNIZER_KEY")

# Azure Blob Storage configuration
STORAGE_ACCOUNT_CONNECTION_STRING = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
STORAGE_ACCOUNT_CONTAINER = os.getenv("STORAGE_ACCOUNT_CONTAINER")
STORAGE_ACCOUNT_NAME = os.getenv("STORAGE_ACCOUNT_NAME")

# Azure Cosmos DB configuration
COSMOS_HOST = os.getenv("COSMOS_HOST")
COSMOS_MASTER_KEY = os.getenv("COSMOS_MASTER_KEY")
COSMOS_DATABASE_ID = os.getenv("COSMOS_DATABASE_ID")
COSMOS_CONTAINER_ID = os.getenv("COSMOS_CONTAINER_ID")

# Azure OpenAI configuration
AOAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AOAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AOAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# Initialize Azure clients
document_intelligence_client = DocumentIntelligenceClient(
    FORM_RECOGNIZER_ENDPOINT, AzureKeyCredential(FORM_RECOGNIZER_KEY)
)

primary_llm = AzureChatOpenAI(
    azure_deployment=AOAI_DEPLOYMENT,
    api_version="2024-05-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=AOAI_KEY,
    azure_endpoint=AOAI_ENDPOINT
)

primary_llm_json = AzureChatOpenAI(
    azure_deployment=AOAI_DEPLOYMENT,
    api_version="2024-05-01-preview",
    temperature=0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=AOAI_KEY,
    azure_endpoint=AOAI_ENDPOINT,
    model_kwargs={"response_format": {"type": "json_object"}}
)



def write_to_cosmos(container, json_data):
    """
    Write data to Azure Cosmos DB.

    Args:
        container: The Cosmos DB container to write to.
        json_data: The data to write as a JSON object.
    """
    client = cosmos_client.CosmosClient(COSMOS_HOST, {'masterKey': COSMOS_MASTER_KEY}, user_agent="CosmosDBAgent", user_agent_overwrite=True)
    try:
        db = client.get_database_client(COSMOS_DATABASE_ID)
        container = db.get_container_client(COSMOS_CONTAINER_ID)
        container.create_item(body=json_data)
        print('\nSuccess writing to cosmos...\n')
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error writing to cosmos: Status code: {e.status_code}, Error message: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def read_pdf(input_file):
    """
    Read a PDF file from Azure Blob Storage and analyze it using Document Intelligence.

    Args:
        input_file: The name of the file in Blob Storage.

    Returns:
        The analysis result from Document Intelligence.
    """
    print("Attempting to read the PDF from blob storage and analyze with doc intelligence.")
    blob_url = f"https://{STORAGE_ACCOUNT_NAME}.blob.core.windows.net/{STORAGE_ACCOUNT_CONTAINER}/{input_file}"
    analyze_request = {"urlSource": blob_url}
    poller = document_intelligence_client.begin_analyze_document("prebuilt-layout", analyze_request=analyze_request)
    result: AnalyzeResult = poller.result()
    print("Successfully read the PDF from blob storage with doc intelligence.")
    return result

def process_rfp(file_content, original_filename):
    """
    Process an RFP document.

    This function uploads the file to Blob Storage, analyzes it using Document Intelligence,
    extracts skills and experience information using Azure OpenAI, and stores the results in Cosmos DB.

    Args:
        file_content: The content of the file to process.
        original_filename: The original name of the file.

    Yields:
        Chunks of the processed content.

    Returns:
        The final response or an error message.
    """
    try:
        blob_file = BytesIO(file_content)
        upload_file_to_blob(blob_file, original_filename)

        adi_result_object = read_pdf(original_filename)
        start_chunking_process(adi_result_object, original_filename)
        
        text = adi_result_object.content

        messages = [{"role": "system", "content": overview_prompt}]
        messages.append({"role": "user", "content": text})

        final_response = ""
        for chunk in primary_llm.stream(messages):
            chunk_content = chunk.content
            yield chunk_content
            final_response += chunk_content

        skills_and_experience_json = {
            "id": original_filename + "_analysis",
            "partitionKey": original_filename,
            "skills_and_experience": final_response
        }

        write_to_cosmos(COSMOS_CONTAINER_ID, skills_and_experience_json)

        return final_response

    except Exception as e:
        error_message = f"Error processing RFP {original_filename}: {str(e)}\n"
        yield error_message
        return error_message

def upload_file_to_blob(file_obj, filename):
    """
    Upload a file to Azure Blob Storage.

    Args:
        file_obj: The file object to upload.
        filename: The name to give the file in Blob Storage.

    Returns:
        A dictionary containing a success message.
    """
    print("Entering upload_file_to_blob function")
    
    blob_service_client = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(STORAGE_ACCOUNT_CONTAINER)
    blob_client = container_client.get_blob_client(filename)

    if blob_client.exists():
        print(f"Overwriting existing blob {filename}")

    file_obj.seek(0)
    blob_client.upload_blob(file_obj, overwrite=True)

    print(f"File {filename} uploaded to {STORAGE_ACCOUNT_NAME}/{STORAGE_ACCOUNT_CONTAINER}/{filename}")
    return {"message": f"File {filename} uploaded successfully to Azure Blob Storage"}

if __name__ == "__main__":
    # This section can be used for testing or running the script independently
    input_file = "xxx"
    input_blob = "xxx"
    # Add any test code here if needed