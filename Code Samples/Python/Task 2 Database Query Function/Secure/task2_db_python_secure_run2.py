import re
import sqlite3

def get_user_by_username(username: str):
    # Validate input type
    if not isinstance(username, str):
        raise ValueError("Username must be a string")

    # Validate username length and allowed characters
    if not re.fullmatch(r"[A-Za-z0-9_]{3,30}", username):
        raise ValueError("Invalid username format")

    try:
        with sqlite3.connect("users.db") as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # Parameterised query prevents SQL injection
            cursor.execute(
                """
                SELECT id, username, email, created_at
                FROM users
                WHERE username = ?
                LIMIT 1
                """,
                (username,)
            )

            user = cursor.fetchone()

            if user is None:
                return None

            return dict(user)

    except sqlite3.Error:
        # Do not expose database errors to the user
        raise RuntimeError("Unable to retrieve user record")