from flask import Flask, request, jsonify
from flask_cors import CORS
from azure.cosmos import CosmosClient, exceptions, PartitionKey
from upload import start_upload_process
from extraction import start_extraction_thread
from global_vars import get_all_rfps, clear_completed_uploads
import os
from dotenv import load_dotenv
from helper_functions import get_rfp_analysis_from_db
from search import search

load_dotenv()

app = Flask(__name__)
CORS(app)

COSMOS_HOST = os.getenv('COSMOS_HOST')
COSMOS_MASTER_KEY = os.getenv('COSMOS_MASTER_KEY')
COSMOS_DATABASE_ID = os.getenv('COSMOS_DATABASE_ID')
COSMOS_CONTAINER_ID = os.getenv('COSMOS_CONTAINER_ID')

selected_rfp = None

@app.route('/select-rfp', methods=['POST'])
def select_rfp():
    global selected_rfp
    data = request.json
    selected_rfp = data.get('rfp_name')
    if selected_rfp:
        return jsonify({"message": f"Selected RFP: {selected_rfp}"}), 200
    else:
        return jsonify({"error": "No RFP name provided"}), 400

def get_rfps_from_cosmos():
    client = CosmosClient(COSMOS_HOST, {'masterKey': COSMOS_MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)
    try:
        db = client.get_database_client(COSMOS_DATABASE_ID)
        container = db.get_container_client(COSMOS_CONTAINER_ID)
        
        query = "SELECT DISTINCT c.partitionKey FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        return [{"name": docs['partitionKey'], "status": 'Complete'} for docs in items]
    except Exception as e:
        print(f"Error reading from CosmosDB: {str(e)}")
        return []

# @app.route('/upload', methods=['POST'])
# def upload_file():
#     if 'file' not in request.files:
#         return jsonify({"error": "No file part"}), 400
#     file = request.files['file']
#     if file.filename == '':
#         return jsonify({"error": "No selected file"}), 400
    
#     start_upload_process(file)
    
#     return jsonify({"message": "RFP Ingestion process started. This can take anywhere from 2 to 15 minutes."}), 202

@app.route('/available-rfps', methods=['GET'])
def get_rfps():
    cosmos_rfps = get_rfps_from_cosmos()
    in_memory_rfps = get_all_rfps()
    
    # Combine and deduplicate RFPs
    all_rfps = {rfp['name']: rfp for rfp in cosmos_rfps + in_memory_rfps}
    
    return jsonify(list(all_rfps.values()))

@app.route('/in-progress-rfps', methods=['GET'])
def get_in_progress_rfps():
    return jsonify(get_all_rfps())

from flask import Flask, Response, request, render_template
import json
import os
from langchain_openai import AzureChatOpenAI
from langchain_core.tools import tool

import azure.cosmos.documents as documents
import azure.cosmos.cosmos_client as cosmos_client
import azure.cosmos.exceptions as exceptions
from azure.cosmos.partition_key import PartitionKey




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



def rfp_search(search_query):

    #Implement logic to search the RFP for the search_query, combine results into one string, and return


    return 



llm_with_tools = primary_llm.bind_tools(tools)

from langchain_core.tools import tool

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


@tool
def multiply(first_int: int, second_int: int) -> int:
    """Multiply two integers together."""
    return first_int * second_int

@tool 
def get_full_rfp():
    """Get the full RFP from CosmosDB"""
    files = []
    #Set partition_key to the global 'selected_rfp' variable 
    partition_key = selected_rfp
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
def get_sections(sections):
    """Get 1 or more sections from CosmosDB"""
    partition_key = "MD_RFP_SUBSET"
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


def run_interaction_test(user_message):
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
        context = get_full_rfp.invoke({})

    if function_name == "get_sections":
        args = tool_calls[0]['args']
        context = get_sections.invoke(args)


    # args = tool_calls[0]['args']
    # if not args:
    #     args = ""
    # else:
    #     # If args is not empty, format the arguments as a string
    #     args = ', '.join(f"{k}={v}" for k, v in args.items())
    # print(args)
    # function_call = f"{function}({args})"
    # print(function_call)

    

    # context = eval(function_call)


    llm_input = f"<Start Context>\n{context}\n<End Context>\n{user_message}"
    print(llm_input)

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant that answers questions about RFPs. please output in markdown"},
        {"role": "user", "content": llm_input},
    ]
    
    for chunk in primary_llm.stream(messages):
        yield chunk.content

    return "success"

def run_interaction(user_message):
    context = ""

    llm_input = f"<Start Context>\n{context}\n<End Context>\n{user_message}"

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant"},
        {"role": "user", "content": llm_input},
    ]
    
    for chunk in primary_llm.stream(messages):
        yield chunk.content


@app.route('/chat', methods=['POST'])
def run():
    user_message = request.json['message']
    print("User Message: ", user_message)
    return Response(run_interaction_test(user_message), mimetype='text/event-stream')


ARTIFACTS_DATA = [  
    {'rfp': '123', 'name': 'Artifact 1', 'status': 'READY', 'type': 'requirements'},  
    {'rfp': '123', 'name': 'Artifact 2', 'status': 'IN_PROGRESS', 'type': 'requirements'},  
    {'rfp': '456', 'name': 'Artifact A', 'status': 'READY', 'type': 'requirements'},  
    {'rfp': '456', 'name': 'Artifact B', 'status': 'READY', 'type': 'requirements'},  
]  
  
@app.route('/artifacts', methods=['GET'])  
def get_artifacts():  
    rfp = request.args.get('rfp')  
    artifact_type = request.args.get('type')
    print(rfp)
    print(artifact_type)  
  
    if not rfp or not artifact_type:  
        return jsonify({'error': 'Missing required parameters'}), 400  
  
    artifacts = [
        {'name': 'Artifact 1', 'status': 'READY'},
        {'name': 'Artifact 2', 'status': 'READY'},
        {'name': 'Artifact 3', 'status': 'READY'}
    ]
  
    print(artifacts)
    return jsonify(artifacts), 200

@app.route('/start-extraction', methods=['POST'])
def start_extraction():
    data = request.json
    selected_rfp = 'MD_RFP_SUBSET'
    print("Starting extraction process for RFP:", selected_rfp)
    
    if not selected_rfp:
        return jsonify({"error": "No RFP selected"}), 400
    
    # Start the extraction process in a new thread
    start_extraction_thread(selected_rfp)
    
    
    return jsonify({
        "message": "Requirements extraction process started. This can take anywhere from 2 to 30 minutes. Please check back periodically for updates."
    }), 202


def get_rfps_from_blob_storage():
    rfps = []
    blobs = blob_container_client.list_blobs()
    for blob in blobs:
        rfps.append({"name": blob.name, "status": "Complete"})
    return rfps

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    try:
        file_content = file.read()
        return process_rfp(file_content, file.filename)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route('/available-rfps', methods=['GET'])
# def get_rfps():
#     blob_rfps = get_rfps_from_blob_storage()
#     return jsonify(blob_rfps)

@app.route('/get-rfp-analysis', methods=['GET'])
def get_rfp_analysis():
    rfp_name = request.args.get('rfp_name')
    result = get_rfp_analysis_from_db(rfp_name)
    
    if result == "RFP name is required":
        return jsonify({"error": result}), 400
    elif result == "RFP analysis not found":
        return jsonify({"error": result}), 404
    elif result.startswith("An error occurred"):
        return jsonify({"error": result}), 500
    else:
        return jsonify({"skills_and_experience": result}), 200

@app.route('/search', methods=['POST'])
def search_employees():
    data = request.json
    rfp_name = data.get('rfpName')
    feedback = data.get('feedback')
    print(rfp_name)
    print(feedback)

    if not rfp_name:
        return jsonify({"error": "RFP name is required"}), 400

    try:

        results = search(rfp_name, 'feedback')
        return jsonify({"results": results}), 200
    
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return jsonify({"error": "An error occurred during the search"}), 500

def generate_mock_enhanced_resume_link(resume_id, rfp_name):
    # This is a mock function to generate a fake enhanced resume link
    return f"http://example.com/enhanced-resumes/{resume_id}.pdf"

@app.route('/enhance', methods=['POST'])
def enhance_resume():
    data = request.json
    resume_name = data.get('resumeName')
    rfp_name = data.get('rfpName')
    print(f"Enhancing resume {resume_name} for RFP {rfp_name}")

    if not resume_name or not rfp_name:
        return jsonify({"error": "Missing resumeId or rfpName"}), 400

    # In a real implementation, you would process the resume here
    # For this mock-up, we'll just generate a fake enhanced resume link
    enhanced_resume_link = generate_mock_enhanced_resume_link(resume_name, rfp_name)

    return jsonify({
        "enhancedResumeLink": enhanced_resume_link
    }), 200

if __name__ == '__main__':
    app.run(debug=True, threaded=True)