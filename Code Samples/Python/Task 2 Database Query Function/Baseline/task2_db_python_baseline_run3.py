import sqlite3

def get_user_by_username(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    query = "SELECT * FROM users WHERE username = ?"
    cursor.execute(query, (username,))

    user = cursor.fetchone()

    conn.close()

    return user