from flask import Flask, request
from werkzeug.utils import secure_filename
from pathlib import Path
import os
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = Path("uploads").resolve()
UPLOAD_FOLDER.mkdir(exist_ok=True)

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB limit

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "pdf"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        return "No file provided", 400

    uploaded_file = request.files["file"]

    if uploaded_file.filename == "":
        return "No file selected", 400

    if not allowed_file(uploaded_file.filename):
        return "File type not allowed", 400

    original_filename = secure_filename(uploaded_file.filename)

    if original_filename == "":
        return "Invalid filename", 400

    file_extension = original_filename.rsplit(".", 1)[1].lower()

    safe_filename = f"{uuid.uuid4().hex}.{file_extension}"

    destination = app.config["UPLOAD_FOLDER"] / safe_filename
    destination = destination.resolve()

    if not str(destination).startswith(str(app.config["UPLOAD_FOLDER"])):
        return "Invalid upload path", 400

    uploaded_file.save(destination)

    return {
        "message": "File uploaded successfully",
        "filename": safe_filename
    }, 201


if __name__ == "__main__":
    app.run(debug=False)