from markitdown import MarkItDown

from flask_cors import CORS
from flask import Flask, request, abort, jsonify
import socket
import os

md = MarkItDown()

app = Flask(__name__)

DOMAIN = os.getenv("CORS_DOMAIN")
SECRET = os.getenv("MARK_IT_DOWN_SECRET")

# Enable CORS for all domains (or configure it to allow only specific domains)
CORS(app, origins=[DOMAIN])

@app.before_request
def check_secret_token():
    if request.method == "OPTIONS":
        return '', 200
    token = request.headers.get("X-WeLearnin-Token")
    if token != SECRET:
        abort(403, description="Forbidden")
        
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain'
}

def allowed_file(file):
    ext_allowed = file.filename.lower().endswith(('.pdf', '.docx', '.pptx', '.txt'))
    mime_allowed = file.mimetype in ALLOWED_MIME_TYPES
    return ext_allowed and mime_allowed

@app.route('/extract', methods=['POST'])
def extract_text():
      # Ensure that 'file' is in the incoming request
    if 'file' not in request.files:
        print("no file part")
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    # Check if the file is valid and allowed
    if file and allowed_file(file):
        try:
            print("Incoming file:", request.files)
            if 'file' not in request.files:
                return jsonify({'error': 'No file part'}), 400

            file = request.files['file']
            print("Received file:", file.filename, file.mimetype)

            if file and allowed_file(file):
                file.stream.seek(0)
                result = md.convert_stream(file.stream)
                return jsonify({
                    'message': 'File processed successfully',
                    'text': getattr(result, "text_content", "")
                })

            return jsonify({'error': 'Invalid file type'}), 400
        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Internal Server Error: {str(e)}'}), 500

    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    print("Hostname:", socket.gethostname())
    app.run(debug=True, host="0.0.0.0", port=5000)  # Expose on port 5000