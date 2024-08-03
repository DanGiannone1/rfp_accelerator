import os  
from dotenv import load_dotenv  
from azure.core.credentials import AzureKeyCredential  
from azure.ai.formrecognizer import DocumentAnalysisClient  
from openai import AzureOpenAI  
from prompts import *
import re
from concurrent.futures import ThreadPoolExecutor
load_dotenv()
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey


COSMOS_HOST = os.getenv("COSMOS_HOST")
COSMOS_MASTER_KEY = os.getenv("COSMOS_MASTER_KEY")
COSMOS_DATABASE_ID = os.getenv("COSMOS_DATABASE_ID")
COSMOS_CONTAINER_ID = os.getenv("COSMOS_CONTAINER_ID")


form_recognizer_endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
form_recognizer_key = os.getenv("FORM_RECOGNIZER_KEY")


document_analysis_client = DocumentAnalysisClient(
    endpoint=form_recognizer_endpoint, credential=AzureKeyCredential(form_recognizer_key)
)


log_file = "D:/temp/conduent/log_de.txt"

class RFP:
    def __init__(self, filename):
        self.rfp_text = None
        self.filename = filename
        self.content_dict = {}
        self.table_of_contents = ""
        self.requirements_dict = {}
    

    def initialize(self):
        """
        Function to initialize the RFP class. Load all relevant data from Cosmos into memory
        Input: filename - the name of the RFP file
        """

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

        print("Loading data for ", self.filename, " from Cosmos...")
        items = list(container.query_items(
            query="SELECT * FROM r WHERE r.partitionKey=@filename",
            parameters=[
                { "name":"@filename", "value": self.filename }
            ]
        ))

        print('Found {0} items'.format(items.__len__()))

        for doc in items:
            id = doc.get('id')
            section_id = doc.get('section_id')
            section_content = doc.get('section_content')
            requirements = doc.get('requirements')
            table_of_contents = doc.get('table_of_contents')
            if section_id is not None and section_content is not None:
                self.content_dict[section_id] = section_content
            if table_of_contents is not None:
                self.table_of_contents = table_of_contents
            if requirements is not None:
                self.requirements_dict[section_id] = requirements
                print("Requirements for ", section_id, " - ", requirements)


    def get_full_text(self):
        """
        Function to get the full text of the RFP
        """
        full_text = ""
        for key in self.content_dict:
            full_text += self.content_dict[key]

        
        return full_text

        




if __name__ == "__main__":
    

    input_file = "D:/temp/conduent/MD_RFP.pdf"
    output_file_path = "D:/temp/conduent/" 
    filename = "MD_RFP"
    

    #Create new RFP class instance 
    rfp = RFP(filename)
    #rfp.read_pdf()
   # rfp.set_table_of_contents(md_toc)
    #rfp.set_valid_sections()
    #rfp.populate_sections()
    rfp.initialize()

    for key in rfp.content_dict:
        print(key)
    
    #upload_to_cosmos()
    


    # item_list = list(container.read_all_items(max_item_count=10))

    # print('Found {0} items'.format(item_list.__len__()))

    # for doc in item_list:
    #     section_id = doc.get('section_id')
    #     section_content = doc.get('section_content')
    #     rfp.content_dict[section_id] = section_content

    # print("Successfully loaded content from cosmos")
    
    


    exit()

    #Read input file
    rfp_text = read_pdf(input_file)
    print("Successfully read the PDF")

    # counter = 0
    # for paragraph in processed_pdf.paragraphs:
    #     print(f"{paragraph.role}: {paragraph.content}")
    #     counter += 1
    #     if counter == 1000:
    #         break

    extraction_doc_intelligence_method(rfp_text)

    #Get table of contents
    # table_of_contents = get_toc(processed_pdf)
    # print("Table of Contents: ", table_of_contents)
    
    # rfp_content_dict = chunk_by_section(processed_pdf, table_of_contents)

    
