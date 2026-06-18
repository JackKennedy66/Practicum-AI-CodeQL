from flask import Flask, request, render_template_string, abort
from pathlib import Path
import re
import html

app = Flask(__name__)

# Only files inside this folder can be viewed
BASE_DIR = Path("files").resolve()

# Allow only safe filenames, e.g. notes.txt, report-1.log
FILENAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]+$")

MAX_FILE_SIZE = 1024 * 1024  # 1 MB

HTML = """
<!doctype html>
<html>
<head>
    <title>Secure File Viewer</title>
</head>
<body>
    <h2>Secure File Viewer</h2>

    <form method="POST">
        <label for="filename">Enter filename:</label>
        <input id="filename" name="filename" type="text" maxlength="100" required>
        <button type="submit">View File</button>
    </form>

    {% if content %}
        <h3>File Contents</h3>
        <pre>{{ content }}</pre>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def view_file():
    content = None

    if request.method == "POST":
        filename = request.form.get("filename", "").strip()

        # Validate input
        if not filename:
            abort(400, "Filename is required")

        if len(filename) > 100:
            abort(400, "Filename is too long")

        if not FILENAME_PATTERN.fullmatch(filename):
            abort(400, "Invalid filename")

        file_path = (BASE_DIR / filename).resolve()

        # Prevent path traversal
        if BASE_DIR not in file_path.parents:
            abort(403, "Access denied")

        if not file_path.is_file():
            abort(404, "File not found")

        if file_path.stat().st_size > MAX_FILE_SIZE:
            abort(413, "File is too large")

        try:
            raw_content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            abort(400, "Only UTF-8 text files can be viewed")

        # Escape output to prevent XSS
        content = html.escape(raw_content)

    return render_template_string(HTML, content=content)


if __name__ == "__main__":
    BASE_DIR.mkdir(exist_ok=True)
    app.run(debug=False)