
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



aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
aoai_key = os.getenv("AZURE_OPENAI_API_KEY")
aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")


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



def extract_structured_data(filename):
    try:

        print("Extracting structured data from RFP...")
       
        

        print("Structured data extraction complete")
      

    except Exception as e:
        print(f"Error processing RFP {filename}: {str(e)}")
        

    return

def start_extraction_thread(rfp_name):
    
    
    try:

        # Submit the task to the thread pool
        executor.submit(extract_structured_data, rfp_name)
        
        return jsonify({"message": "Extraction process started. This can take anywhere from 2 to 30 minutes depending on the size of the RFP."}), 202
    except Exception as e:
        print(f"Error starting upload process: {str(e)}")
        return jsonify({"error": "Failed to start upload process"}), 500

if __name__ == "__main__":
    

    rfp_name = "MD_RFP_SUBSET.pdf"
    
    extract_structured_data(input_file)



    exit()