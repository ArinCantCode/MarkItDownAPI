from markitdown import MarkItDown

from flask_cors import CORS
from flask import Flask, request, jsonify

md = MarkItDown()

app = Flask(__name__)

DOMAIN = os.getenv("CORS_DOMAIN")
SECRET = os.getenv("WELEARNIN_SECRET")

# Enable CORS for all domains (or configure it to allow only specific domains)
CORS(app, origins=[DOMAIN])

@app.before_request
def check_secret_token():
    token = request.headers.get("X-WeLearnin-Token")
    if token != SECRET:
        abort(403, description="Forbidden");

ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain'
}

def allowed_file(file):
    """
    Check if the file's MIME type is allowed.
    """
    return file.mimetype in ALLOWED_MIME_TYPES

@app.route('/extract', methods=['POST'])
def extract_text():
      # Ensure that 'file' is in the incoming request
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    # Add more cases for other file types...

    # Check if the file is valid and allowed
    if file and allowed_file(file):
        try:
            result = md.convert_stream(file.stream)
            return jsonify({
                'message': 'File processed successfully',
                'text': result.text_content  # Assuming result has 'text_content'
            })
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return jsonify({'error': 'Invalid file type'}), 400

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)  # Expose on port 5000