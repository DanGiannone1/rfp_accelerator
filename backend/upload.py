"""
###upload.py###

Upload and processing module for RFP documents.

This module handles the uploading of RFP documents to Azure Data Lake Storage Gen2,
processing them using Azure Document Intelligence, and analyzing the content
using Azure OpenAI. It also manages writing the analysis results to Azure Cosmos DB.

This module calls "chunking.py" to chunk the RFP into sections. 
"""

# Standard library imports
import os
from io import BytesIO

# Third-party imports
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Local imports
from common.adls import ADLSManager
from common.cosmosdb import CosmosDBManager
from chunking import start_chunking_process
from prompts import overview_prompt

# Load environment variables
load_dotenv()

# Azure Form Recognizer configuration
FORM_RECOGNIZER_ENDPOINT = os.getenv("FORM_RECOGNIZER_ENDPOINT")
FORM_RECOGNIZER_KEY = os.getenv("FORM_RECOGNIZER_KEY")

# Azure OpenAI configuration
AOAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AOAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AOAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# Initialize managers and clients
adls_manager = ADLSManager()
cosmos_db = CosmosDBManager()
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

def read_pdf(input_file):
    """
    Read a PDF file from Azure Data Lake Storage and analyze it using Document Intelligence.

    Args:
        input_file: The name of the file in ADLS.

    Returns:
        The analysis result from Document Intelligence.
    """
    print("Attempting to read the PDF from ADLS and analyze with doc intelligence.")
    storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")
    storage_account_container = os.getenv("STORAGE_ACCOUNT_CONTAINER")
    
    blob_url = f"https://{storage_account_name}.blob.core.windows.net/{storage_account_container}/{input_file}"
    analyze_request = {"urlSource": blob_url}
    poller = document_intelligence_client.begin_analyze_document("prebuilt-layout", analyze_request=analyze_request)
    result = poller.result()
    print("Successfully read the PDF from ADLS with doc intelligence.")
    return result

def process_rfp(file_content, original_filename):
    """
    Process an RFP document.

    This function uploads the file to ADLS, analyzes it using Document Intelligence,
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
        # Upload file to ADLS
        upload_result = adls_manager.upload_to_blob(file_content, original_filename)
        print(f"Upload result: {upload_result['message']}")

        # Process with Document Intelligence
        adi_result_object = read_pdf(original_filename)
        start_chunking_process(adi_result_object, original_filename)
        
        text = adi_result_object.content

        # Generate analysis using Azure OpenAI
        messages = [{"role": "system", "content": overview_prompt}]
        messages.append({"role": "user", "content": text})

        final_response = ""
        for chunk in primary_llm.stream(messages):
            chunk_content = chunk.content
            yield chunk_content
            final_response += chunk_content

        # Store analysis in Cosmos DB
        skills_and_experience_json = {
            "id": original_filename + "_analysis",
            "partitionKey": original_filename,
            "skills_and_experience": final_response
        }

        cosmos_db.create_item(skills_and_experience_json)

        return final_response

    except Exception as e:
        error_message = f"Error processing RFP {original_filename}: {str(e)}\n"
        yield error_message
        return error_message

if __name__ == "__main__":
    # This section can be used for testing or running the script independently
    pass