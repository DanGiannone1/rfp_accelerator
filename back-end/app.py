from flask import Flask, request, jsonify
from flask_cors import CORS
from azure.cosmos import CosmosClient, exceptions, PartitionKey
from upload import start_upload_process
from global_vars import get_all_rfps, clear_completed_uploads
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

COSMOS_HOST = os.getenv('COSMOS_HOST')
COSMOS_MASTER_KEY = os.getenv('COSMOS_MASTER_KEY')
COSMOS_DATABASE_ID = os.getenv('COSMOS_DATABASE_ID')
COSMOS_CONTAINER_ID = os.getenv('COSMOS_CONTAINER_ID')

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

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    
    start_upload_process(file)
    
    return jsonify({"message": "File upload started"}), 202

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

if __name__ == '__main__':
    app.run(debug=True, threaded=True)