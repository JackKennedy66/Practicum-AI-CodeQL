from flask import Flask, request, render_template_string, abort
from pathlib import Path

app = Flask(__name__)

BASE_DIR = Path("files").resolve()

HTML = """
<h2>View a File</h2>

<form method="POST">
    <label>Enter filename:</label>
    <input type="text" name="filename" required>
    <button type="submit">View</button>
</form>

{% if content %}
    <h3>File Contents:</h3>
    <pre>{{ content }}</pre>
{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def view_file():
    content = None

    if request.method == "POST":
        filename = request.form.get("filename", "").strip()

        if not filename:
            abort(400, "Filename is required")

        file_path = (BASE_DIR / filename).resolve()

        # Prevent path traversal attacks
        if not str(file_path).startswith(str(BASE_DIR)):
            abort(403, "Access denied")

        if not file_path.is_file():
            abort(404, "File not found")

        try:
            content = file_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            abort(400, "Only text files can be viewed")

    return render_template_string(HTML, content=content)


if __name__ == "__main__":
    BASE_DIR.mkdir(exist_ok=True)
    app.run(debug=False)