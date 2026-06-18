from flask import Flask, request, render_template_string, abort
import sqlite3
import re
from html import escape

app = Flask(__name__)
DATABASE = "users.db"

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{1,30}$")

HTML = """
<!doctype html>
<html>
<head>
    <title>User Search</title>
</head>
<body>
    <h2>Search Users</h2>

    <form method="GET" action="/search">
        <input type="text" name="username" maxlength="30" required>
        <button type="submit">Search</button>
    </form>

    {% if searched %}
        <h3>Results</h3>
        {% if users %}
            <ul>
            {% for user in users %}
                <li>{{ user["username"] }}</li>
            {% endfor %}
            </ul>
        {% else %}
            <p>No users found.</p>
        {% endif %}
    {% endif %}
</body>
</html>
"""

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template_string(HTML, searched=False, users=[])

@app.route("/search")
def search_users():
    username = request.args.get("username", "").strip()

    if not username:
        return render_template_string(HTML, searched=False, users=[])

    if not USERNAME_REGEX.fullmatch(username):
        abort(400, description="Invalid username format")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT username
            FROM users
            WHERE username LIKE ?
            LIMIT 20
            """,
            (f"%{username}%",)
        )

        users = cursor.fetchall()

    except sqlite3.Error:
        abort(500, description="Database error")

    finally:
        if "conn" in locals():
            conn.close()

    return render_template_string(
        HTML,
        searched=True,
        users=users
    )

if __name__ == "__main__":
    app.run(debug=False)