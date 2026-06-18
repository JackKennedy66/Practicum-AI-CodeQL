# secure_file_upload_handler.py

from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf", "txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_FILE_SIZE

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def allowed_file(filename):
    """
    Checks that the uploaded file has an allowed extension.
    """
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def upload_file():
    """
    Secure file upload handler.
    Follows OWASP-style protections:
    - Validates file presence
    - Restricts allowed file types
    - Limits file size
    - Sanitises the original filename
    - Renames the uploaded file using a UUID
    - Prevents path traversal
    """

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "File type not allowed"}), 400

    original_filename = secure_filename(file.filename)

    if original_filename == "":
        return jsonify({"error": "Invalid filename"}), 400

    extension = original_filename.rsplit(".", 1)[1].lower()
    safe_filename = f"{uuid.uuid4().hex}.{extension}"

    upload_path = os.path.abspath(app.config["UPLOAD_FOLDER"])
    file_path = os.path.abspath(os.path.join(upload_path, safe_filename))

    if not file_path.startswith(upload_path):
        return jsonify({"error": "Invalid file path"}), 400

    file.save(file_path)

    return jsonify({
        "message": "File uploaded securely",
        "stored_filename": safe_filename
    }), 200


if __name__ == "__main__":
    app.run(debug=False)