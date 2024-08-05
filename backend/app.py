from flask import Flask, request, jsonify
from flask_cors import CORS
from upload import upload_rfp

app = Flask(__name__)
CORS(app)  # This enables CORS for all routes

ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file and allowed_file(file.filename):
        # Directly pass the file object to upload_rfp
        result = upload_rfp(file)
        return jsonify({'message': 'File successfully processed', 'result': result}), 200
    return jsonify({'error': 'File type not allowed'}), 400

if __name__ == '__main__':
    app.run(debug=True)