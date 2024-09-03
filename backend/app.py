"""
Flask application for RFP processing and analysis.

This application provides various endpoints for uploading, processing, and analyzing
Request for Proposal (RFP) documents. It integrates with Azure Cosmos DB, Azure AI Search, Azure Document Intelligence, and Azure OpenAI.
"""

# Standard library imports
import json
import os

# Third-party imports
from azure.cosmos import CosmosClient, exceptions
from azure.cosmos.partition_key import PartitionKey
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, make_response, request
from flask_cors import CORS
from langchain_openai import AzureChatOpenAI

# Local imports
from chat import run_interaction
from extraction import get_extraction_progress, start_extraction_thread
from global_vars import get_all_rfps
from helper_functions import get_rfp_analysis_from_db
from response import respond_to_requirement
from search import search
from upload import process_rfp

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Azure Cosmos DB configuration
COSMOS_HOST = os.getenv('COSMOS_HOST')
COSMOS_MASTER_KEY = os.getenv('COSMOS_MASTER_KEY')
COSMOS_DATABASE_ID = os.getenv('COSMOS_DATABASE_ID')
COSMOS_CONTAINER_ID = os.getenv('COSMOS_CONTAINER_ID')

# Azure Blob Storage configuration
STORAGE_ACCOUNT_CONNECTION_STRING = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
STORAGE_ACCOUNT_CONTAINER = os.getenv("STORAGE_ACCOUNT_CONTAINER")
STORAGE_ACCOUNT_RESUME_CONTAINER = os.getenv("STORAGE_ACCOUNT_RESUME_CONTAINER")

# Azure OpenAI configuration
AOAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
AOAI_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AOAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")

# Initialize Azure clients
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_CONNECTION_STRING)
blob_container_client = blob_service_client.get_container_client(STORAGE_ACCOUNT_CONTAINER)
blob_resume_container_client = blob_service_client.get_container_client(STORAGE_ACCOUNT_RESUME_CONTAINER)

cosmos_client = CosmosClient(COSMOS_HOST, {'masterKey': COSMOS_MASTER_KEY}, user_agent="CosmosDBPythonQuickstart", user_agent_overwrite=True)

# Initialize Cosmos DB database and container
try:
    db = cosmos_client.create_database(id=COSMOS_DATABASE_ID)
    print(f'Database with id \'{COSMOS_DATABASE_ID}\' created')
except exceptions.CosmosResourceExistsError:
    db = cosmos_client.get_database_client(COSMOS_DATABASE_ID)
    print(f'Database with id \'{COSMOS_DATABASE_ID}\' was found')

try:
    container = db.create_container(id=COSMOS_CONTAINER_ID, partition_key=PartitionKey(path='/partitionKey'))
    print(f'Container with id \'{COSMOS_CONTAINER_ID}\' created')
except exceptions.CosmosResourceExistsError:
    container = db.get_container_client(COSMOS_CONTAINER_ID)
    print(f'Container with id \'{COSMOS_CONTAINER_ID}\' was found')

# Global variables
selected_rfp = None

# Helper functions
def get_rfps_from_cosmos():
    """Fetch RFPs from Cosmos DB."""
    try:
        query = "SELECT DISTINCT c.partitionKey FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        return [{"name": docs['partitionKey'], "status": 'Complete'} for docs in items]
    except Exception as e:
        print(f"Error reading from CosmosDB: {str(e)}")
        return []

def get_rfps_from_blob_storage():
    """Fetch RFPs from Azure Blob Storage."""
    rfps = []
    blobs = blob_container_client.list_blobs()
    for blob in blobs:
        rfps.append({"name": blob.name, "status": "Complete"})
    return rfps

# Routes
@app.route('/select-rfp', methods=['POST'])
def select_rfp():
    """Select an RFP for processing."""
    global selected_rfp
    data = request.json
    selected_rfp = data.get('rfp_name')
    if selected_rfp:
        return jsonify({"message": f"Selected RFP: {selected_rfp}"}), 200
    else:
        return jsonify({"error": "No RFP name provided"}), 400

@app.route('/available-rfps', methods=['GET'])
def get_rfps():
    """Get a list of available RFPs."""
    cosmos_rfps = get_rfps_from_cosmos()
    in_memory_rfps = get_all_rfps()
    all_rfps = {rfp['name']: rfp for rfp in cosmos_rfps + in_memory_rfps}
    return jsonify(list(all_rfps.values()))

@app.route('/in-progress-rfps', methods=['GET'])
def get_in_progress_rfps():
    """Get a list of RFPs currently being processed."""
    return jsonify(get_all_rfps())

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload and process an RFP file."""
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

@app.route('/chat', methods=['POST'])
def run():
    """Handle chat interactions."""
    data = request.json
    user_message = data['message']
    rfp_name = data['rfp_name']
    print(f"User Message: {user_message}, RFP Name: {rfp_name}")
    return Response(run_interaction(user_message, rfp_name), mimetype='text/event-stream')

@app.route('/get-rfp-sections', methods=['GET'])
def get_rfp_sections():
    """Get sections of a specific RFP."""
    rfp_name = request.args.get('rfp_name')
    if not rfp_name:
        return jsonify({"error": "RFP name is required"}), 400

    try:
        query = f"SELECT * FROM c WHERE c.partitionKey = '{rfp_name}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        if not items:
            return jsonify({"error": "No sections found for the specified RFP"}), 404
        
        sections = []
        for item in items:
            section_id = item.get('section_id')
            section_content = item.get('section_content')
            
            if section_id and section_content:
                section = {
                    "section_id": section_id,
                    "content": section_content,
                    "requirements": []
                }
                
                requirements = item.get('requirements', {}).get('output', [])
                for req in requirements:
                    if isinstance(req, dict):
                        section["requirements"].append({
                            "section_name": req.get('section_name', ''),
                            "page_number": req.get('page_number', ''),
                            "section_number": req.get('section_number', ''),
                            "content": req.get('content', ''),
                            "is_requirement": req.get('is_requirement', 'no')
                        })
                
                sections.append(section)
        
        return jsonify({"sections": sections}), 200
    except Exception as e:
        print(f"Error fetching RFP sections: {str(e)}")
        return jsonify({"error": "An error occurred while fetching RFP sections"}), 500

@app.route('/get-requirements', methods=['GET'])
def get_requirements():
    """Get requirements for a specific RFP."""
    rfp_name = request.args.get('rfp_name')
    if not rfp_name:
        return jsonify({"error": "RFP name is required"}), 400

    try:
        query = f"SELECT c.requirements.output FROM c WHERE c.partitionKey = '{rfp_name}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        
        if not items:
            return jsonify({"error": "No requirements found for the specified RFP"}), 404
        
        all_requirements = []
        for item in items:
            if 'output' in item:
                requirements = [req for req in item['output'] if req.get('is_requirement') == 'yes']
                all_requirements.extend(requirements)
        
        return jsonify({"requirements": all_requirements}), 200
    except Exception as e:
        print(f"Error fetching requirements: {str(e)}")
        return jsonify({"error": "An error occurred while fetching requirements"}), 500

@app.route('/update-requirements', methods=['POST'])
def update_requirements():
    """Update requirements for a specific RFP section."""
    data = request.json
    rfp_name = data.get('rfp_name')
    section_id = data.get('section_id')
    requirements = data.get('requirements')

    if not all([rfp_name, section_id, requirements]):
        return jsonify({"error": "Missing required data"}), 400

    try:
        query = f"SELECT * FROM c WHERE c.partitionKey = '{rfp_name}' AND c.section_id = '{section_id}'"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))

        if not items:
            return jsonify({"error": "Section not found"}), 404

        doc = items[0]
        doc['requirements'] = requirements
        doc['reviewed'] = True

        container.replace_item(item=doc, body=doc)

        return jsonify({"message": "Requirements updated and section marked as reviewed"}), 200

    except exceptions.CosmosHttpResponseError as e:
        print(f"An error occurred: {e.message}")
        return jsonify({"error": "An error occurred while updating the database"}), 500

@app.route('/respond-to-requirement', methods=['POST'])
def response_to_requirement():
    """Generate a response to a specific requirement."""
    data = request.json
    requirement = data.get('requirement')
    user_message = data.get('user_message', '')
    
    if not requirement:
        return jsonify({"error": "Requirement is required"}), 400

    try:
        return Response(respond_to_requirement(user_message, requirement), mimetype='text/event-stream')
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return jsonify({"error": "An error occurred while generating the response"}), 500

@app.route('/progress', methods=['GET'])
def get_progress():
    """Get progress of RFP processing."""
    rfp_name = request.args.get('rfp_name')
    
    if not rfp_name:
        return jsonify({"error": "No RFP name provided"}), 400
    
    try:
        total_query = f"SELECT VALUE COUNT(1) FROM c WHERE c.partitionKey = '{rfp_name}' AND IS_DEFINED(c.section_content)"
        extracted_query = f"SELECT VALUE COUNT(1) FROM c WHERE c.partitionKey = '{rfp_name}' AND IS_DEFINED(c.requirements) AND IS_DEFINED(c.section_content)"
        reviewed_query = f"SELECT VALUE COUNT(1) FROM c WHERE c.partitionKey = '{rfp_name}' AND c.reviewed = true AND IS_DEFINED(c.section_content)"

        total_count = list(container.query_items(query=total_query, enable_cross_partition_query=True))[0]
        extracted_count = list(container.query_items(query=extracted_query, enable_cross_partition_query=True))[0]
        reviewed_count = list(container.query_items(query=reviewed_query, enable_cross_partition_query=True))[0]

        extraction_progress = (extracted_count / total_count) * 100 if total_count > 0 else 0
        review_progress = (reviewed_count / total_count) * 100 if total_count > 0 else 0

        return jsonify({
            "extraction_progress": extraction_progress,
            "review_progress": review_progress
        }), 200

    except Exception as e:
        print(f"Error fetching progress: {str(e)}")
        return jsonify({"error": "An error occurred while fetching progress"}), 500

@app.route('/get-rfp-analysis', methods=['GET'])
def get_rfp_analysis():
    """Get analysis for a specific RFP."""
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
    """Search for employees based on RFP requirements."""
    data = request.json
    rfp_name = data.get('rfpName')
    feedback = data.get('feedback')

    if not rfp_name:
        return jsonify({"error": "RFP name is required"}), 400

    try:
        results = search(rfp_name, feedback)
        return jsonify({"results": results}), 200
    except Exception as e:
        print(f"Error during search: {str(e)}")
        return jsonify({"error": "An error occurred during the search"}), 500

@app.route('/resume', methods=['GET'])
def get_resume():
    """Get a resume PDF file."""
    resume_name = request.args.get('resumeName')[:-4] + 'pdf'
  
    blob_client = blob_resume_container_client.get_blob_client('pdf/' + resume_name)
    download_stream = blob_client.download_blob()
    file_content = download_stream.readall()
    
    if file_content:
        response = make_response(file_content)
        response.headers['Content-Type'] = 'application/pdf'
        return response
    else:
        return make_response('Failed to download file', 500)
    


@app.route('/download', methods=['GET'])
def download_resume():
    resume_name = request.args.get('resumeName')
  
    blob_client = blob_resume_container_client.get_blob_client('processed/' + resume_name)
    download_stream = blob_client.download_blob()
    file_content = download_stream.readall()
    
    if file_content:
        response = make_response(file_content)
        response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        return response
    else:
        return make_response('Failed to download file', 500)


@app.route('/start-extraction', methods=['POST'])
def start_extraction():
    data = request.json
    rfp_name = data.get('rfp_name')
    
    if not rfp_name:
        return jsonify({"error": "No RFP name provided"}), 400
    
    start_extraction_thread(rfp_name)
    
    return jsonify({
        "message": "Requirements extraction process started. This can take some time. Please check back periodically for updates."
    }), 202

@app.route('/extraction-progress', methods=['GET'])
def extraction_progress():
    rfp_name = request.args.get('rfp_name')
    
    if not rfp_name:
        return jsonify({"error": "No RFP name provided"}), 400
    
    progress = get_extraction_progress(rfp_name)
    
    return jsonify({
        "progress": progress
    }), 200

if __name__ == '__main__':
    app.run(debug=True, threaded=True)