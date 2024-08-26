
import os  
from dotenv import load_dotenv  
import re
from concurrent.futures import ThreadPoolExecutor
import time
from werkzeug.datastructures import FileStorage
from io import BytesIO
import json
import threading
from global_vars import add_in_progress_upload, remove_in_progress_upload, set_upload_error

from langchain_openai import AzureChatOpenAI

from prompts import *
from rfp import *

from azure.core.credentials import AzureKeyCredential  
from azure.identity import DefaultAzureCredential, ClientSecretCredential

from azure.ai.formrecognizer import DocumentAnalysisClient, AnalyzeResult 
from azure.eventhub import EventHubProducerClient, EventData   
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient, ContentSettings
from azure.storage.filedatalake import (
    DataLakeServiceClient,
    DataLakeDirectoryClient,
    FileSystemClient
)

from flask import jsonify
from werkzeug.utils import secure_filename
import concurrent.futures
import logging
import io


# Create a ThreadPoolExecutor
executor = concurrent.futures.ThreadPoolExecutor(max_workers=5)

load_dotenv()

form_recognizer_endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
form_recognizer_key = os.getenv("FORM_RECOGNIZER_KEY")
print("Form Recognizer Endpoint: ", form_recognizer_endpoint)
print("Form Recognizer Key: ", form_recognizer_key)


connect_str = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
container_name = os.getenv("STORAGE_ACCOUNT_CONTAINER")
storage_account_name = os.getenv("STORAGE_ACCOUNT_NAME")


eventstreamConnectionString = os.getenv("EVENTSTREAM_CONNECTION_STRING")

document_analysis_client = DocumentAnalysisClient(
    endpoint=form_recognizer_endpoint, credential=AzureKeyCredential(form_recognizer_key)
)

aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
aoai_key = os.getenv("AZURE_OPENAI_API_KEY")
aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

print("Azure OpenAI Deployment: ", aoai_deployment)
print("Azure OpenAI Key: ", aoai_key)
print("Azure OpenAI Endpoint: ", aoai_endpoint)

COSMOS_HOST = os.getenv("COSMOS_HOST")
COSMOS_MASTER_KEY = os.getenv("COSMOS_MASTER_KEY")
COSMOS_DATABASE_ID = os.getenv("COSMOS_DATABASE_ID")
COSMOS_CONTAINER_ID = os.getenv("COSMOS_CONTAINER_ID")


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


def write_to_fabric(filename):


    print(f'Attempting to upload {filename} to fabric...')
    # Set your account, workspace, and item path here

    

    credential = ClientSecretCredential(

        tenant_id=os.getenv('TENANT_ID'),

        client_id=os.getenv('CLIENT_ID'),

        client_secret=os.getenv('CLIENT_SECRET')

        )

    LOCAL_PATH = "D:/temp/data/"
    LOCAL_PATH_DATA = LOCAL_PATH + "data_files/"
    LOCAL_PATH_METADATA = LOCAL_PATH + "metadata/"
    SERIES_FILE = LOCAL_PATH + "config/fred_series_ids.txt"
    WORKSPACE_NAME = "dangiannone-dev"
    LAKEHOUSE_PATH = "djg_lakehouse.Lakehouse/Files/fred/"
    LAKEHOUSE_PATH_METADATA = "djg_lakehouse.Lakehouse/Files/metadata/"
    ACCOUNT_NAME = "onelake"

    workspace = "dangiannone-dev"
    lakehouse = "djg_lakehouse"

    files_directory = 'rfp'

    # service_client = DataLakeServiceClient(account_url='https://onelake.dfs.fabric.microsoft.com/', credential=credential)
    # file_system_client = service_client.get_file_system_client(file_system = workspace)

    # paths = file_system_client.get_paths(path=f'{lakehouse}.Lakehouse/Files/{files_directory}')
    
    # for path in paths:
    #     print(path.name)

    #abfss://345ac8dd-4538-458f-ad26-3e04ac2794a8@daily-onelake.dfs.fabric.microsoft.com/b46760c3-c6fa-483e-989d-8291e2a57c90/Files

    account_url = f"https://{ACCOUNT_NAME}.dfs.fabric.microsoft.com"
    token_credential = DefaultAzureCredential()

    # service_client = DataLakeServiceClient(account_url="{}://{}.dfs.fabric.microsoft.com".format("https", ACCOUNT_NAME), credential=token_credential)

    # file_system_client = service_client.get_file_system_client(WORKSPACE_NAME)
    # paths = file_system_client.get_paths(lakehouse_path)

    # for path in paths:
    #      print(path.name + '\n')

    # #with open(LOCAL_FILE, "rb") as local_file:

    # #Read file contents into a variable

    # #print(series_data)

    # file_system_client.create_file(lakehouse_path + file_name)
    # file_client = file_system_client.get_file_client(lakehouse_path + file_name)
        
    # file_client.append_data(data=series_data, offset=0, length=len(series_data))
    # file_client.flush_data(len(series_data))



def upload_file_to_blob(file_obj):
    """
    Uploads a file to Azure Blob Storage
    Inputs:
    - file_obj: the file object to upload
    - connect_str: the connection string for Azure Blob Storage
    - container_name: the name of the container in Azure Blob Storage
    - storage_account_name: the name of the storage account
    """
    
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create a container client
    container_client = blob_service_client.get_container_client(container_name)

    # Extract the file name from the file object
    file_name = file_obj.filename



    # Create blob client
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    # Create a blob client using the file name as the blob name
    blob_client = container_client.get_blob_client(file_obj.filename)

    if blob_client.exists():
        print(f"Blob {file_name} already exists in {container_name}.")
        # Handle the case where the blob exists (e.g., skip, overwrite, or prompt the user)
        # For this example, we'll skip the upload
        return {"message": f"File {file_name} already exists in Azure Blob Storage"}
    # Upload the file
    blob_client.upload_blob(file_obj.read(), overwrite=True)

        

    # Upload the file
    #blob_client.upload_blob(file_obj.stream, overwrite=True)

    print(f"File {file_name} uploaded to {storage_account_name}/{container_name}/{file_name}")
    return {"message": f"File {file_obj.filename} uploaded successfully to Azure Blob Storage"}


def write_to_eventstream(event_data):

   

    # Create a producer client to send messages to the event hub.  
    producer = EventHubProducerClient.from_connection_string(conn_str=eventstreamConnectionString)  
    
    # Create a batch.  
    event_data_batch = producer.create_batch()  
    

    
        # Add the data to the batch.  
    try:  
            event_data_batch.add(EventData(event_data))  
            print('data added to batch')  
    except ValueError:  
            # The batch has reached its maximum size, send it and create a new one.  
            producer.send_batch(event_data_batch)  
            print('Batch sent to event stream')  
            event_data_batch = producer.create_batch()  
            event_data_batch.add(EventData(event_data))    
            print('data added to batch') 

    # Don't forget to send the last batch if it has any events in it.  
    if len(event_data_batch) > 0:  
        producer.send_batch(event_data_batch)  
        print('Final batch sent to event stream')  
    
    producer.close()  

def inference(llm, messages, step, json_mode=False):
    
        start_time = time.time()
        # messages = [{"role": "system", "content": "You are a helpful AI assistant. always respond in json format with your thought process and answer."}]
        # messages.append([{"role": "user", "content": "What is 2+2?"}])

        # if json_mode:
        #     llm.bind(response_format={"type": "json_object"})
            


        raw_response = llm.invoke(messages)
        end_time = time.time()
        latency = end_time - start_time
        
        response = raw_response.content
        #print("Response: ", response)

        if json_mode:
            response = json.loads(raw_response.content)
            

        messages.append({"role": "assistant", "content": response})

        telemetry = {
            "step_name": step, 
            "step_type": "llm",
            "endpoint": llm.azure_endpoint,
            "deployment": llm.deployment_name,
            "version": llm.openai_api_version, 
            "messages": messages,
            "tokens": raw_response.usage_metadata,
            "latency": latency

        }
        #step_telemetry.append(telemetry)
        #cosmos_db.write_to_cosmos(telemetry)
        return response




def standardize_page_number(page_number):  
    """  
    Function to standardize the page number  
    """  
    messages = [{"role": "system", "content": page_number_prompt},
                {"role": "user", "content": page_number}]
    standardized_page_number = inference(primary_llm, messages, "standardize_page_number")
    #print("Standardizing  ", page_number, " to " , standardized_page_number)

    return standardized_page_number

    
def dict_to_json(filename, key, value):

    #id = filename - key with any special characters replaced with spaces
    id = filename + " - " + key
    id = re.sub(r'[/#]', ' ', id)
    print("Generating JSON for ", filename, " - ", key)
    json = {'id' : filename + " - " + key,
            'partitionKey' : filename,
            'section_id' : key,
            'section_content' : value
            }
    return json


def write_to_cosmos(container, json):
    

    # Create a SalesOrder object. This object has nested properties and various types including numbers, DateTimes and strings.
    # This can be saved as JSON as is without converting into rows/columns.
    try:
        container.create_item(body=json)
        print('\nSuccess writing to cosmos...\n')
    except exceptions.CosmosHttpResponseError as e:
        print("Error writing to cosmos")
        print(f"Status code: {e.status_code}, Error message: {e.message}")
    except Exception as e:
        print("An unexpected error occurred")
        print(str(e))


def upload_to_cosmos(filename, content_dict, table_of_contents):

    #Setup connection
    client = cosmos_client.CosmosClient(COSMOS_HOST, {'masterKey': COSMOS_MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    try:
        # setup database for this sample
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


    print("Loading sections to Cosmos...")
    for key in content_dict:
         #print(key, " - ", rfp.content_dict[key])
         json = dict_to_json(filename, key, content_dict[key])
         write_to_cosmos(container, json)

    toc_json = {
        'id' : filename + " - TOC",
        'partitionKey' : filename,
        'table_of_contents' : table_of_contents
    }
    write_to_cosmos(container, toc_json)
    print("Loading table of contents to Cosmos...")



# RDC - Refactor to use blob storage
def read_pdf(input_file):  
        """
        Function to read the PDF file from Azure Blob Storage and analyze it using Azure Document Intelligence
        Input:
        - input_file: name of the PDF to use 
        Output:
        - result: The result object from Azure Document Intelligence
        """
        
        # we need to use the document_analysis_client.begin_analyze_document_from_url method to read the PDF from blob storage
        blob_url = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{input_file}"

        # blob_url2 = "https://stgrfpdemo.blob.core.windows.net/rfp/MD_RFP_SUBSET%201.pdf"
        # poller = document_analysis_client.begin_analyze_document_from_url(model_id="prebuilt-layout", document_url=input_file)
        
        # poller = document_analysis_client.begin_analyze_document("prebuilt-layout", AnalyzeDocumentRequest(url_source=blob_url))       
        
        poller = document_analysis_client.begin_analyze_document_from_url("prebuilt-layout", blob_url)  

        result = poller.result()
        print("Successfully read the PDF from blob storage and analyzed.")
        return result

def validate_section(section, table_of_contents):  
        """  
        Function to validate the section number  
        """  
        section_and_toc = f"Table of Contents: {table_of_contents} \n\nSection to validate: {section}"
        messages = [{"role": "system", "content": section_validator_prompt},
                    {"role": "user", "content": section_and_toc}]

        result = inference(primary_llm_json, messages, "section_validation", json_mode=True)
        print(f'{section} - {result["thought_process"]} - {result["answer"]}')

        is_section_valid = result["answer"]
        return is_section_valid

def get_table_of_contents(adi_result_object):  
        """
        Function to extract the table of contents from the RFP
        Input Args: 
            1. adi_result_object - the result object from Azure Document Intelligence
            
        Output: table_of_contents - the table of contents extracted from the RFP (str)
        """
        
        first_pages = get_pages(adi_result_object, 1, 12)
        messages = [{"role": "system", "content": toc_prompt},
                    {"role": "user", "content": first_pages}]
        table_of_contents = inference(primary_llm, messages, "toc_extraction")
        print("Table of Contents: ", table_of_contents)
        return table_of_contents


def get_pages(adi_result_object, x, y):  
        """
        Function to get the content of a range of pages from the RFP
        Inputs: 
            adi_result_object - the result object from Azure Document Intelligence
            x - the start page
            y - the end page
        Output: page_range_text - the content of the pages in the range (str)
        """
        page_range_text = ""
        for page in adi_result_object.pages[x:y]:  
            for line in page.lines:  
                page_range_text += line.content + "\n"
        return page_range_text

def set_valid_sections(adi_result_object, table_of_contents):  
        """
        Function that uses the LLM to validate the section headings derived from Azure Document Intelligence
        We load all the section headings as keys to the self.content_dict dictionary. We then kick off the validate_section function for each section heading in parallel. 
        Each invalid section is added to the invalid_sections list. At the end, we delete the invalid sections from the self.content_dict dictionary.
        Input: self.rfp_text - the result object from Azure Document Intelligence
        Output: self.content_dict - key will be populated with valid sections, value will be empty string. This is populated in the populate_sections function.
        """
        invalid_sections = set()
        content_dict = {}

        # Populate content_dict
        for paragraph in adi_result_object.paragraphs:
            if paragraph.role == "title" or paragraph.role == "sectionHeading":
                content_dict[paragraph.content] = ""

        # Create a ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=1) as executor:
            # Run validate_section for each section heading in parallel
            # Prepare a tuple of (section, table_of_contents) for each key in content_dict
            section_args = ((section, table_of_contents) for section in content_dict.keys())
            validation_results = list(executor.map(lambda args: validate_section(*args), section_args))


        # Iterate over content_dict.keys() and validation_results together
        for section, result in zip(content_dict.keys(), validation_results):
            # If the result is 'no', add the section to invalid_sections
            if result.lower() == 'no':
                invalid_sections.add(section)

        # Remove invalid sections from content_dict
        for section in invalid_sections:
            print(f"Removing invalid section: {section}")
            del content_dict[section]

        return content_dict


def populate_sections(adi_result_object, content_dict):
        """
        Function to populate the content_dict dictionary with the content for each section heading
        Input: self.rfp_text - the result object from Azure Document Intelligence
               self.content_dict - the dictionary of section headings
        Output: self.content_dict - key will be populated with valid sections, value will be the content of the section
        """
        current_key = None
        page_number = ""
        page_number_found = False

        for paragraph in adi_result_object.paragraphs:
            # Check if we see a new section heading. If it is in self.content_dict, we know it is a valid heading. 
            if (paragraph.role == "title" or paragraph.role == "sectionHeading") and paragraph.content in content_dict:
                # If the section heading is valid, set the current key to the section heading
                if current_key is not None:
                    #We have reached the start of a new section. If we haven't found a page number for the last section, append it. 
                    if page_number_found == False:
                        content_dict[current_key] += "Page Number: " + str(page_number) + "\n"
                else:
                    print("Current key is none so this is the first section: " + paragraph.content)
                        
                current_key = paragraph.content
                content_dict[current_key] = ""
                page_number_found = False

            #Process each paragraph. Headers and Footers are skipped as they do not contain anything of value generally. 
            #When we find a page number, we add it to the content of the current section and then add 1 to it (since we are then on the next page). 
            if current_key is not None:
                if paragraph.role == "pageHeader" or paragraph.role == "pageFooter":
                    continue
                if paragraph.role == "pageNumber":
                    page_number_found = True
                    #print("Found page number: ", paragraph.content)
                    page_number = standardize_page_number(paragraph.content)
                    content_dict[current_key] += "Page Number: " + page_number + "\n"
                    try:
                        #print("incrementing page number from ", page_number, " to " , int(page_number) + 1)
                        page_number = int(page_number) + 1
                    except ValueError as e:
                        pass
                        #print("Error message:", e)
                        #print(f"page number {page_number} not an integer")
                    continue
                content_dict[current_key] += paragraph.content + "\n"

        return content_dict



def upload_rfp(file_content, original_filename):
    try:
        print(f"Starting to process file: {original_filename}")
        add_in_progress_upload(original_filename)

        # Create a BytesIO object for blob storage upload
        blob_file = io.BytesIO(file_content)
        
        # Upload to blob storage
        upload_file_to_blob(blob_file, original_filename)
        print("File uploaded to blob storage")

        # Process the file
        print("Reading PDF")
        #pdf_file = io.BytesIO(file_content)
        adi_result_object = read_pdf(original_filename)
        print("PDF read complete")

        print("Getting table of contents")
        table_of_contents = get_table_of_contents(adi_result_object)
        print("Table of contents retrieved")

        print("Setting valid sections")
        content_dict = set_valid_sections(adi_result_object, table_of_contents)
        print("Valid sections set")

        print("Populating sections")
        content_dict = populate_sections(adi_result_object, content_dict)
        print("Sections populated")

        print("Uploading to Cosmos DB")
        upload_to_cosmos(original_filename, content_dict, table_of_contents) 
        print("Upload to Cosmos DB complete")
        
        remove_in_progress_upload(original_filename)
        print("In-progress upload removed")

    except Exception as e:
        print(f"Error processing RFP {original_filename}: {str(e)}")
        set_upload_error(original_filename)

    return

def start_upload_process(file):
    original_filename = secure_filename(file.filename)
    
    try:
        # Read file content
        file_content = file.read()
        
        # Submit the task to the thread pool
        executor.submit(upload_rfp, file_content, original_filename)
        
        return jsonify({"message": "RFP Ingestion process started. This can take anywhere from 2 to 15 minutes."}), 202
    except Exception as e:
        print(f"Error starting upload process: {str(e)}")
        return jsonify({"error": "Failed to start upload process"}), 500

def upload_file_to_blob(file_obj, filename):
    """
    Uploads a file to Azure Blob Storage
    Inputs:
    - file_obj: BytesIO object containing file content
    - filename: name of the file in blob storage
    """
    print("Entering upload_file_to_blob function")
    
    # Create the BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)

    # Create a container client
    container_client = blob_service_client.get_container_client(container_name)

    # Create blob client
    blob_client = container_client.get_blob_client(filename)

    if blob_client.exists():
        print(f"Blob {filename} already exists in {container_name}.")
        print(f"Overwriting existing blob {filename}")

    # Upload the file
    file_obj.seek(0)
    blob_client.upload_blob(file_obj, overwrite=True)

    print(f"File {filename} uploaded to {storage_account_name}/{container_name}/{filename}")
    return {"message": f"File {filename} uploaded successfully to Azure Blob Storage"}

if __name__ == "__main__":
    

    input_file = "C:/temp/data/MD_RFP_SUBSET4.pdf"
    input_blob = "https://stgrfpdemo.blob.core.windows.net/rfp/MD_RFP_SUBSET_1.pdf"
    
    
    upload_rfp(input_file)



    exit()