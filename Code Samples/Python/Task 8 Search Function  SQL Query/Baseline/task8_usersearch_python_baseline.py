from flask import Flask, request, render_template_string
import sqlite3
import re

app = Flask(__name__)

DATABASE = "users.db"

HTML = """
<h2>Search Users</h2>

<form method="GET" action="/search">
    <input type="text" name="username" placeholder="Enter username">
    <button type="submit">Search</button>
</form>

{% if users %}
    <h3>Results:</h3>
    <ul>
    {% for user in users %}
        <li>{{ user[1] }} - {{ user[2] }}</li>
    {% endfor %}
    </ul>
{% elif searched %}
    <p>No users found.</p>
{% endif %}
"""

def get_db_connection():
    return sqlite3.connect(DATABASE)

@app.route("/")
def index():
    return render_template_string(HTML)

@app.route("/search")
def search_users():
    username = request.args.get("username", "").strip()
    users = []

    if not username:
        return render_template_string(HTML, users=[], searched=False)

    if not re.match(r"^[a-zA-Z0-9_]{1,30}$", username):
        return "Invalid username format", 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, email FROM users WHERE username LIKE ?",
        (f"%{username}%",)
    )

    users = cursor.fetchall()
    conn.close()

    return render_template_string(HTML, users=users, searched=True)

if __name__ == "__main__":
    app.run(debug=False)