"""
Chunking module for processing RFP documents.

This module handles the chunking of RFP documents, including extracting the table of contents,
validating sections, and uploading the processed content to Azure Cosmos DB using the centralized
CosmosDBManager.
"""

# Standard library imports
import json
import os
import threading
from concurrent.futures import ThreadPoolExecutor

# Third-party imports
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI

# Local imports
from common.cosmosdb import CosmosDBManager
from prompts import toc_prompt, section_validator_prompt_with_toc

# Load environment variables
load_dotenv()

# Azure OpenAI configuration
AOAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AOAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AOAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# Initialize CosmosDBManager
cosmos_manager = CosmosDBManager()

# Initialize Azure OpenAI clients
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

def get_table_of_contents(adi_result_object):
    """
    Extract the table of contents from the document.

    Args:
        adi_result_object: The document analysis result object.

    Returns:
        str: The extracted table of contents.
    """
    first_pages = adi_result_object.content[:5000]  # Adjust as needed
    messages = [
        {"role": "system", "content": toc_prompt},
        {"role": "user", "content": first_pages}
    ]
    
    table_of_contents = primary_llm.invoke(messages)
    print("Table of Contents: ", table_of_contents)
    return table_of_contents.content

def validate_section(section, table_of_contents):
    """
    Validate a section of the document.

    Args:
        section: The section to validate.
        table_of_contents: The extracted table of contents.

    Returns:
        str or None: The validation result ('yes' or 'no') or None if there's an error.
    """
    section_and_toc = f"Table of Contents: {table_of_contents} \n\nSection to validate: {section}"
    messages = [
        {"role": "system", "content": section_validator_prompt_with_toc},
        {"role": "user", "content": section_and_toc}
    ]

    raw_response = primary_llm_json.invoke(messages)
    try:
        result_json = json.loads(raw_response.content)
        thought_process = result_json.get("thought_process")
        answer = result_json.get("answer")
        print(f"Section: {section}")
        print(f"Thought process: {thought_process}")
        print(f"Answer: {answer}")
        print("\n\n\n****************")
        return answer
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error loading JSON or extracting fields: {e}. Section in question: {section}")
        return None

def set_valid_sections(adi_result_object, table_of_contents):
    """
    Determine valid sections in the document.

    Args:
        adi_result_object: The document analysis result object.
        table_of_contents: The extracted table of contents.

    Returns:
        dict: A dictionary of valid sections and their content.
    """
    content_dict = {}

    for paragraph in adi_result_object.paragraphs:
        if paragraph.role in ["title", "sectionHeading"]:
            content_dict[paragraph.content] = ""

    with ThreadPoolExecutor(max_workers=3) as executor:
        section_args = ((section, table_of_contents) for section in content_dict.keys())
        validation_results = list(executor.map(lambda args: validate_section(*args), section_args))

    print("Completed initial validation of section headings")
    invalid_sections = set()
    for section, result in zip(content_dict.keys(), validation_results):
        if result and result.lower() == 'no':
            invalid_sections.add(section)

    for section in invalid_sections:
        print(f"Removing invalid section: {section}")
        del content_dict[section]

    return content_dict

def populate_sections(adi_result_object, content_dict):
    """
    Populate the content of each valid section.

    Args:
        adi_result_object: The document analysis result object.
        content_dict: A dictionary of valid sections.

    Returns:
        dict: The updated content dictionary with populated sections.
    """
    current_key = None
    page_number = ""
    page_number_found = False

    for paragraph in adi_result_object.paragraphs:
        if paragraph.role in ["title", "sectionHeading"] and paragraph.content in content_dict:
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

def upload_to_cosmos(filename, content_dict, table_of_contents):
    """
    Upload processed document sections and table of contents to Cosmos DB.

    Args:
        filename: The name of the original file.
        content_dict: A dictionary of document sections and their content.
        table_of_contents: The extracted table of contents.
    """
    try:
        # Upload sections
        for key, value in content_dict.items():
            json_data = {
                'id': f"{filename} - {key}",
                'partitionKey': filename,
                'section_id': key,
                'section_content': value
            }
            cosmos_manager.create_item(json_data)

        # Upload table of contents
        toc_json = {
            'id': f"{filename} - TOC",
            'partitionKey': filename,
            'table_of_contents': table_of_contents
        }
        cosmos_manager.create_item(toc_json)
        print("Loading table of contents to Cosmos...")
        
    except Exception as e:
        print(f"Error uploading to Cosmos DB: {str(e)}")

def chunking(adi_result_object, original_filename):
    """
    Process the document by chunking it into sections and uploading to Cosmos DB.

    Args:
        adi_result_object: The document analysis result object.
        original_filename: The name of the original file.
    """
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

def start_chunking_process(adi_result_object, original_filename):
    """
    Start the chunking process in a background thread.

    Args:
        adi_result_object: The document analysis result object.
        original_filename: The name of the original file.
    """
    threading.Thread(target=chunking, args=(adi_result_object, original_filename)).start()