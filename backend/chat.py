import os
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool
import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey

load_dotenv()

COSMOS_HOST = os.getenv('COSMOS_HOST')
COSMOS_MASTER_KEY = os.getenv('COSMOS_MASTER_KEY')
COSMOS_DATABASE_ID = os.getenv('COSMOS_DATABASE_ID')
COSMOS_CONTAINER_ID = os.getenv('COSMOS_CONTAINER_ID')

aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
aoai_key = os.getenv("AZURE_OPENAI_API_KEY")
aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")

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

tools = [
    {
        "name": "search",
        "description": "search the RFP for information. Use this tool when a user asks a question that is not specific to a particular section, but rather a general question about the RFP.",
        "parameters": {
            "type": "object",
            "properties": {
                "search_query": {"type": "string", "description": "The search query to use"}
            },
            "required": ["search_query"]
        }
    },
    {
        "name": "get_sections",
        "description": "Pull specific sections from the database. Use this tool when a user asks a question that is specific to a particular section or sections",
        "parameters": {
            "type": "object",
            "properties": {
                "sections": {"type": "string", "description": "the sections to pull"}
            },
            "required": ["sections"]
        }
    },
    {
        "name": "get_full_rfp",
        "description": "Pull the full RFP from the database. Use this tool when a user asks a question that can only be answered by looking at the full document",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
]

llm_with_tools = primary_llm.bind_tools(tools)

client = cosmos_client.CosmosClient(COSMOS_HOST, {'masterKey': COSMOS_MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
try:
    db = client.get_database_client(COSMOS_DATABASE_ID)
    container = db.get_container_client(COSMOS_CONTAINER_ID)
except exceptions.CosmosHttpResponseError as e:
    print('\nrun_sample has caught an error. {0}'.format(e.message))

@tool
def get_full_rfp(rfp_name):
    """Get the full RFP from CosmosDB"""
    files = []
    partition_key = rfp_name
    print(partition_key)
    context = ""
    try:
        print(f"Fetching files from CosmosDB for partitionKey: {partition_key}")
        query = f"SELECT * FROM c WHERE c.partitionKey = '{partition_key}' AND IS_DEFINED(c.section_content)"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        print(f"Found {len(items)} files in CosmosDB for partitionKey: {partition_key} with section_content")
        for item in items:
            files.append(item)
        for file in files:
            context += file['section_content']
        return context
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error reading from CosmosDB: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
    
    return context

@tool
def get_sections(sections, rfp_name):
    """Get 1 or more sections from CosmosDB"""
    partition_key = rfp_name
    context = ""
    try:
        print(f"Fetching sections from CosmosDB for partitionKey: {partition_key} and sections: {sections}")
        query = f"SELECT * FROM c WHERE c.partitionKey = '{partition_key}' AND CONTAINS(c.section_id, '{sections}')"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        print(f"Found {len(items)} sections in CosmosDB for partitionKey: {partition_key} with section_header containing '{sections}'")
        for item in items:
            context += item['section_content']
        return context
    except exceptions.CosmosHttpResponseError as e:
        print(f"Error reading from CosmosDB: {e.message}")
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")

    return context

def run_interaction(user_message, rfp_name):
    context = ""

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant. "},
        {"role": "user", "content": user_message},
    ]

    print("Deciding what to do...")
    raw_response = llm_with_tools.invoke(messages)
    tool_calls = raw_response.tool_calls
    print(tool_calls)
    function_name = tool_calls[0]['name']

    if function_name == "get_full_rfp":
        context = get_full_rfp(rfp_name)

    if function_name == "get_sections":
        args = tool_calls[0]['args']
        combined_args = {
            "sections": args['sections'],
            "rfp_name": rfp_name
        }
        context = get_sections.invoke(combined_args)

    llm_input = f"<Start Context>\n{context}\n<End Context>\n{user_message}"
    print(llm_input)

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant that answers questions about RFPs. please output in markdown"},
        {"role": "user", "content": llm_input},
    ]
    
    for chunk in primary_llm.stream(messages):
        yield chunk.content

    return "success"

