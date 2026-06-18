import re
import sqlite3
from typing import Optional, Tuple

USERNAME_REGEX = re.compile(r"^[A-Za-z0-9_]{3,30}$")

def get_user_by_username(db_path: str, username: str) -> Optional[Tuple]:
    """
    Securely retrieves a user record from the database by username.
    """

    if not isinstance(username, str):
        raise ValueError("Username must be a string")

    username = username.strip()

    if not USERNAME_REGEX.fullmatch(username):
        raise ValueError("Invalid username format")

    query = """
        SELECT id, username, email, created_at
        FROM users
        WHERE username = ?
        LIMIT 1
    """

    try:
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(query, (username,))
            user = cursor.fetchone()

            if user is None:
                return None

            return tuple(user)

    except sqlite3.Error:
        raise RuntimeError("Database error occurred")