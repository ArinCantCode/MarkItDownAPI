from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from markitdown import MarkItDown
import os
import socket
import traceback

app = Flask(__name__)
md = MarkItDown()

# Load config from env vars
DOMAIN = os.getenv("CORS_DOMAIN", "*")  # fallback to *
SECRET = os.getenv("MARK_IT_DOWN_SECRET", "dev-secret")

# Enable CORS for specific domain
CORS(app, origins=[DOMAIN])

# Allowed MIME types
ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain'
}

def allowed_file(file):
    """Check if the file's MIME type is allowed."""
    ext_allowed = file.filename.lower().endswith(('.pdf', '.docx', '.pptx', '.txt'))
    mime_allowed = file.mimetype in ALLOWED_MIME_TYPES
    return ext_allowed and mime_allowed

@app.before_request
def check_secret_token():
    if request.method == "OPTIONS":
        return '', 200  # Let preflight pass
    token = request.headers.get("X-WeLearnin-Token")
    if token != SECRET:
        abort(403, description="Forbidden")

@app.route('/extract', methods=['POST'])
def extract_text():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400

        file = request.files['file']
        if file and allowed_file(file):
            # Optional: Save file for debugging
            # file.save(f"/tmp/debug-{file.filename}")

            try:
                file.stream.seek(0)
            except Exception:
                pass  # Some streams don't support seek

            result = md.convert_stream(file.stream)

            return jsonify({
                'success': True,
                'message': 'File processed successfully',
                'text': getattr(result, "text_content", "")
            })

        return jsonify({'success': False, 'error': 'Invalid file type'}), 400

    except Exception as e:
        traceback.print_exc()
        return jsonify({'success': False, 'error': f'Internal Server Error: {str(e)}'}), 500

if __name__ == '__main__':
    print("Hostname:", socket.gethostname())
    app.run(debug=True, host="0.0.0.0", port=5000)