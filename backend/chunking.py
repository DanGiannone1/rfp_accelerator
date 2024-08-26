import os
from dotenv import load_dotenv
import concurrent.futures
import threading

from langchain_openai import AzureChatOpenAI

from prompts import toc_prompt, section_validator_prompt

import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import json

load_dotenv()

# Azure OpenAI
aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
aoai_key = os.getenv("AZURE_OPENAI_API_KEY")
aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

# Cosmos DB
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
    raw_response = llm.invoke(messages)
    response = raw_response.content if not json_mode else json.loads(raw_response.content)
    return response

def get_table_of_contents(adi_result_object):
    first_pages = adi_result_object.content[:5000]  # Adjust as needed
    messages = [{"role": "system", "content": toc_prompt},
                {"role": "user", "content": first_pages}]
    table_of_contents = inference(primary_llm, messages, "toc_extraction")
    print("Table of Contents: ", table_of_contents)
    return table_of_contents

def validate_section(section, table_of_contents):
    section_and_toc = f"Table of Contents: {table_of_contents} \n\nSection to validate: {section}"
    messages = [{"role": "system", "content": section_validator_prompt},
                {"role": "user", "content": section_and_toc}]
    result = inference(primary_llm_json, messages, "section_validation", json_mode=True)
    print(f'{section} - {result["thought_process"]} - {result["answer"]}')
    return result["answer"]

def set_valid_sections(adi_result_object, table_of_contents):
    invalid_sections = set()
    content_dict = {}

    for paragraph in adi_result_object.paragraphs:
        if paragraph.role == "title" or paragraph.role == "sectionHeading":
            content_dict[paragraph.content] = ""

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        section_args = ((section, table_of_contents) for section in content_dict.keys())
        validation_results = list(executor.map(lambda args: validate_section(*args), section_args))

    for section, result in zip(content_dict.keys(), validation_results):
        if result.lower() == 'no':
            invalid_sections.add(section)

    for section in invalid_sections:
        print(f"Removing invalid section: {section}")
        del content_dict[section]

    return content_dict

def populate_sections(adi_result_object, content_dict):
    current_key = None
    page_number = ""
    page_number_found = False

    for paragraph in adi_result_object.paragraphs:
        if (paragraph.role == "title" or paragraph.role == "sectionHeading") and paragraph.content in content_dict:
            if current_key is not None and not page_number_found:
                content_dict[current_key] += f"Page Number: {page_number}\n"
            current_key = paragraph.content
            content_dict[current_key] = ""
            page_number_found = False

        if current_key is not None:
            if paragraph.role in ["pageHeader", "pageFooter"]:
                continue
            if paragraph.role == "pageNumber":
                page_number_found = True
                page_number = paragraph.content
                content_dict[current_key] += f"Page Number: {page_number}\n"
                continue
            content_dict[current_key] += paragraph.content + "\n"

    return content_dict

def write_to_cosmos(container, json_data):
    try:
        container.create_item(body=json_data)
        print('\nSuccess writing to cosmos...\n')
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error writing to cosmos: Status code: {e.status_code}, Error message: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

def upload_to_cosmos(filename, content_dict, table_of_contents):
    client = cosmos_client.CosmosClient(COSMOS_HOST, {'masterKey': COSMOS_MASTER_KEY})
    
    try:
        db = client.get_database_client(COSMOS_DATABASE_ID)
        container = db.get_container_client(COSMOS_CONTAINER_ID)
    except exceptions.CosmosResourceNotFoundError:
        print(f"Database or container not found. Please ensure they exist.")
        return

    for key, value in content_dict.items():
        json_data = {
            'id': f"{filename} - {key}",
            'partitionKey': filename,
            'section_id': key,
            'section_content': value
        }
        write_to_cosmos(container, json_data)

    toc_json = {
        'id': f"{filename} - TOC",
        'partitionKey': filename,
        'table_of_contents': table_of_contents
    }
    write_to_cosmos(container, toc_json)
    print("Loading table of contents to Cosmos...")

def chunking(adi_result_object, original_filename):
    try:
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

    except Exception as e:
        print(f"Error in chunking process for {original_filename}: {str(e)}")

# This function can be called from upload.py to start the background chunking process
def start_chunking_process(adi_result_object, original_filename):
    threading.Thread(target=chunking, args=(adi_result_object, original_filename)).start()