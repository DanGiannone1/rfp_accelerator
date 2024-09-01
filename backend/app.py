from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from azure.cosmos import CosmosClient, exceptions, PartitionKey
from upload import process_rfp
from extraction import start_extraction_thread
from global_vars import get_all_rfps, clear_completed_uploads
from extraction import start_extraction_thread, get_extraction_progress
import os
from dotenv import load_dotenv
from helper_functions import get_rfp_analysis_from_db
from search import search
from azure.storage.blob import BlobServiceClient
from chat import run_interaction
from response import respond_to_requirement

load_dotenv()

app = Flask(__name__)
CORS(app)

COSMOS_HOST = os.getenv('COSMOS_HOST')
COSMOS_MASTER_KEY = os.getenv('COSMOS_MASTER_KEY')
COSMOS_DATABASE_ID = os.getenv('COSMOS_DATABASE_ID')
COSMOS_CONTAINER_ID = os.getenv('COSMOS_CONTAINER_ID')

STORAGE_ACCOUNT_CONNECTION_STRING = os.getenv("STORAGE_ACCOUNT_CONNECTION_STRING")
STORAGE_ACCOUNT_CONTAINER = os.getenv("STORAGE_ACCOUNT_CONTAINER")
STORAGE_ACCOUNT_RESUME_CONTAINER = os.getenv("STORAGE_ACCOUNT_RESUME_CONTAINER")
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_ACCOUNT_CONNECTION_STRING)
blob_container_client = blob_service_client.get_container_client(STORAGE_ACCOUNT_CONTAINER)
blob_resume_container_client = blob_service_client.get_container_client(STORAGE_ACCOUNT_RESUME_CONTAINER)


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




@app.route('/chat', methods=['POST'])
def run():
    data = request.json
    user_message = data['message']
    rfp_name = data['rfp_name']
    print(f"User Message: {user_message}, RFP Name: {rfp_name}")
    return Response(run_interaction(user_message, rfp_name), mimetype='text/event-stream')




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

@app.route('/get-requirements', methods=['GET'])
def get_requirements():
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

    
def generate_dummy_response(requirement):
    return f"This is a dummy response for the requirement: '{requirement}'. In a real scenario, this would be generated by an AI model based on the RFP context and any additional instructions provided."

@app.route('/respond-to-requirement', methods=['POST'])
def response_to_requirement():
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