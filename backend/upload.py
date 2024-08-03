
import os  
from dotenv import load_dotenv  
from azure.core.credentials import AzureKeyCredential  
from azure.ai.formrecognizer import DocumentAnalysisClient, AnalyzeResult 
from openai import AzureOpenAI  
import re
from concurrent.futures import ThreadPoolExecutor
load_dotenv()
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey
import time
from langchain_openai import AzureChatOpenAI

from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.storage.blob import ContentSettings
from io import BytesIO
import json
from azure.eventhub import EventHubProducerClient, EventData   

from prompts import *
from rfp import *

md_toc = """1 | Minimum Qualifications | 1 | [1,1]
1.1 | Offeror Minimum Qualifications | 1 | [1,1]
2 | Contractor Requirements: Scope of Work | 2 | [2,30]
2.1 | Summary Statement | 2 | [2,2]
2.2 | Background, Purpose and Goals | 2 | [2,5]
2.3 | Responsibilities and Tasks | 5 | [5,19]
2.4 | Deliverables | 19 | [19,30]
2.5 | Optional Features or Services | 30 | [30,30]
2.6 | Service Level Agreement (SLA) | 30 | [30,30]
3 | Contractor Requirements: General | 38 | [38,65]
3.1 | Contract Initiation Requirements | 38 | [38,38]
3.2 | End of Contract Transition | 38 | [38,40]
3.3 | Invoicing | 40 | [40,43]
3.4 | Liquidated Damages | 43 | [43,43]
3.5 | Disaster Recovery and Data | 43 | [43,44]
3.6 | Insurance Requirements | 44 | [44,45]
3.7 | Security Requirements | 45 | [45,52]
3.8 | Problem Escalation Procedure | 52 | [52,53]
3.9 | SOC 2 Type 2 Audit Report | 53 | [53,54]
3.10 | Experience and Personnel | 54 | [54,60]
3.11 | Substitution of Personnel | 60 | [60,62]
3.12 | Minority Business Enterprise (MBE) Reports | 62 | [62,63]
3.13 | Veteran Small Business Enterprise (VSBE) Reports | 63 | [63,64]
3.14 | Task Orders | 64 | [64,65]
3.15 | Additional Clauses | 65 | [65,65]
4 | Procurement Instructions | 67 | [67,81]
4.1 | Pre-Proposal Conference | 67 | [67,67]
4.2 | eMaryland Marketplace Advantage (eMMA) | 67 | [67,67]
4.3 | Questions | 67 | [67,68]
4.4 | Procurement Method | 68 | [68,68]
4.5 | Proposal Due (Closing) Date and Time | 68 | [68,68]
4.6 | Multiple or Alternate Proposals | 68 | [68,68]
4.7 | Economy of Preparation | 68 | [68,68]
4.8 | Public Information Act Notice | 68 | [68,69]
4.9 | Award Basis | 69 | [69,69]
4.10 | Oral Presentation | 69 | [69,69]
4.11 | Duration of Proposal | 69 | [69,69]
4.12 | Revisions to the RFP | 69 | [69,69]
4.13 | Cancellations | 69 | [69,70]
4.14 | Incurred Expenses | 70 | [70,70]
4.15 | Protest/Disputes | 70 | [70,70]
4.16 | Offeror Responsibilities | 70 | [70,70]
4.17 | Acceptance of Terms and Conditions | 70 | [70,71]
4.18 | Proposal Affidavit | 71 | [71,71]
4.19 | Contract Affidavit | 71 | [71,71]
4.20 | Compliance with Laws/Arrearages | 71 | [71,71]
4.21 | Verification of Registration and Tax Payment | 71 | [71,71]
4.22 | False Statements | 71 | [71,71]
4.23 | Payments by Electronic Funds Transfer | 71 | [71,72]
4.24 | Prompt Payment Policy | 72 | [72,72]
4.25 | Electronic Procurements Authorized | 72 | [72,73]
4.26 | MBE Participation Goal | 73 | [73,76]
4.27 | VSBE Goal | 76 | [76,77]
4.28 | Living Wage Requirements | 77 | [77,79]
4.29 | Federal Funding Acknowledgement | 79 | [79,79]
4.30 | Conflict of Interest Affidavit and Disclosure | 79 | [79,79]
4.31 | Non-Disclosure Agreement | 79 | [79,80]
4.32 | HIPAA - Business Associate Agreement | 80 | [80,80]
4.33 | Nonvisual Access | 80 | [80,81]
4.34 | Mercury and Products That Contain Mercury | 81 | [81,81]
4.35 | Location of the Performance of Services Disclosure | 81 | [81,81]
4.36 | Department of Human Services (DHS) Hiring Agreement | 81 | [81,81]
4.37 | Small Business Reserve (SBR) Procurement | 81 | [81,81]
4.38 | Maryland Healthy Working Families Act Requirements | 81 | [81,81]
5 | Proposal Format | 82 | [82,94]
5.1 | Two Part Submission | 82 | [82,82]
5.2 | Proposal Delivery and Packaging | 82 | [82,82]
5.3 | Volume I - Technical Proposal | 82 | [82,91]
5.4 | Volume II - Financial Proposal | 91 | [91,91]
6 | Evaluation and Selection Process | 92 | [92,94]
6.1 | Evaluation Committee | 92 | [92,92]
6.2 | Technical Proposal Evaluation Criteria | 92 | [92,92]
6.3 | Financial Proposal Evaluation Criteria | 92 | [92,92]
6.4 | Reciprocal Preference | 92 | [92,93]
6.5 | Selection Procedures | 93 | [93,94]
6.6 | Documents Required upon Notice of Recommendation for Contract Award | 94 | [94,94]
7 | RFP ATTACHMENTS AND APPENDICES | 95 | [95,162]
Attachment A | Pre-Proposal Conference Response Form | 99 | [99,99]
Attachment B | Financial Proposal Instructions & Form | 100 | [100,102]
Attachment C | Proposal Affidavit | 102 | [102,103]
Attachment D | Minority Business Enterprise (MBE) Forms | 103 | [103,104]
Attachment E | Veteran-Owned Small Business Enterprise (VSBE) Forms | 104 | [104,105]
Attachment F | Maryland Living Wage Affidavit of Agreement for Service Contracts | 105 | [105,107]
Attachment G | Federal Funds Attachments | 107 | [107,108]
Attachment H | Conflict of Interest Affidavit and Disclosure | 108 | [108,109]
Attachment I | Non-Disclosure Agreement (Contractor) | 109 | [109,110]
Attachment J | HIPAA Business Associate Agreement | 110 | [110,111]
Attachment K | Mercury Affidavit | 111 | [111,112]
Attachment L | Location of the Performance of Services Disclosure | 112 | [112,113]
Attachment M | Contract | 113 | [113,134]
Attachment N | Contract Affidavit | 134 | [134,135]
Attachment O | DHS Hiring Agreement | 135 | [135,136]
Appendix 1 | Abbreviations and Definitions | 136 | [136,140]
Appendix 2 | Offeror Information Sheet | 140 | [140,141]
Appendix 3 | Administrations Program Overview | 141 | [141,153]
Appendix 4 | DHS Customer Service Center Volume Historical Data Sample | 153 | [153,154]
Appendix 5 | DHS IT Systems | 154 | [154,156]
Appendix 6 | Criminal Background Check Affidavit | 156 | [156,157]
Appendix 7 | Annual Internal Revenue Service (IRS) Employee Awareness Acknowledgement | 157 | [157,159]
Appendix 8 | Historical Email Support & Documentation Fulfillment | 159 | [159,162]
"""

form_recognizer_endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
form_recognizer_key = os.getenv("FORM_RECOGNIZER_KEY")
print("Form Recognizer Endpoint: ", form_recognizer_endpoint)
print("Form Recognizer Key: ", form_recognizer_key)

# RDC - Added these environment variables to store the Azure Blob Storage connection string and container name
AZURE_CONNECTION_STRING = os.getenv("RFP_STORAGE_CONNECTION_STRING")
AZURE_CONTAINER_NAME = os.getenv("RFP_AZURE_CONTAINER_NAME")


# RDC Initialize the BlobServiceClient to be used in the upload_file_to_blob function
blob_service_client = BlobServiceClient.from_connection_string(AZURE_CONNECTION_STRING)
container_client = blob_service_client.get_container_client(AZURE_CONTAINER_NAME)

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

log_file = "D:/temp/conduent/log_de.txt"



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

################

def read_pdf(input_file):  
        """
        Function to read the PDF file using Azure Document Intelligence
        Input: input_file - the document
        Output: result - the result object from Azure Document Intelligence
        """
        with open(input_file, "rb") as f:  
            poller = document_analysis_client.begin_analyze_document("prebuilt-layout", f)  
        result = poller.result()  
        print("Successfully read the RFP")
        return result
    
# RDC - Refactor to use blob storage
def read_pdf2(input_file):  
        """
        Function to read the PDF file from Azure Blob Storage and analyze it using Azure Document Intelligence
        Input:
        - input_file: name of the PDF to use 
        Output:
        - result: The result object from Azure Document Intelligence
        """
        AZURE_STORAGE_ACCOUNT = os.getenv("RFP_STORAGE_ACCOUNT2")   
        # we need to use the document_analysis_client.begin_analyze_document_from_url method to read the PDF from blob storage
        blob_url = f"https://{AZURE_STORAGE_ACCOUNT}.blob.core.windows.net/{AZURE_CONTAINER_NAME}/{input_file}"
        blob_url2 = "https://stgrfpdemo.blob.core.windows.net/rfp/MD_RFP_SUBSET%201.pdf"
        poller = document_analysis_client.begin_analyze_document_from_url(model_id="prebuilt-layout", document_url=input_file)
        
        # poller = document_analysis_client.begin_analyze_document("prebuilt-layout",AnalyzeDocumentRequest(url_source=blob_url))       
        
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


def process_rfp(file):

    #Extract the root filename from input_file and remove extension
    print("process_rfp() - Processing file: ", file)
    
    filename = os.path.splitext(os.path.basename(file))[0]
    print("Filename: ", filename)


    adi_result_object = read_pdf(file)

    table_of_contents = md_toc
    #table_of_contents = get_table_of_contents(adi_result_object)

    content_dict = set_valid_sections(adi_result_object, table_of_contents)

    content_dict = populate_sections(adi_result_object, content_dict)
    

    upload_to_cosmos(filename, content_dict, table_of_contents) 

    return

# RDC - Refactor to use blob storage
def process_rfp2(file):

    #Extract the root filename from input_file and remove extension
    print("process_rfp() - Processing file: ", file)
    
    print("Filename: ", file)

    #Create new RFP class instance 
    #rfp = RFP(input_file)

    adi_result_object = read_pdf2(file)

    #table_of_contents = de_toc
    table_of_contents = get_table_of_contents(adi_result_object)

    content_dict = set_valid_sections(adi_result_object, table_of_contents)
 
    content_dict = populate_sections(adi_result_object, content_dict)
    
 
    upload_to_cosmos(file, content_dict, table_of_contents) 

    return



if __name__ == "__main__":
    

    input_file = "C:/temp/data/MD_RFP_SUBSET2.pdf"
    input_blob = "https://stgrfpdemo.blob.core.windows.net/rfp/MD_RFP_SUBSET_1.pdf"
    
    
    process_rfp(input_file)



    exit()