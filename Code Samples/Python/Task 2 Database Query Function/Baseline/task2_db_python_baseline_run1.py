import sqlite3

def get_user_by_username(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, username, email FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    conn.close()

    return user