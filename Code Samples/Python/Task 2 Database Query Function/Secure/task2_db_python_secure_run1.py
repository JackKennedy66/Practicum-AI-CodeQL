import re
import sqlite3
from typing import Optional, Dict, Any

USERNAME_REGEX = re.compile(r"^[a-zA-Z0-9_]{3,30}$")

def get_user_by_username(db_path: str, username: str) -> Optional[Dict[str, Any]]:
    """
    Securely retrieve a user record by username.
    """

    if not isinstance(username, str):
        raise ValueError("Invalid username")

    username = username.strip()

    if not USERNAME_REGEX.fullmatch(username):
        raise ValueError("Username must be 3-30 characters and contain only letters, numbers, or underscores")

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
            row = cursor.fetchone()

            if row is None:
                return None

            return {
                "id": row["id"],
                "username": row["username"],
                "email": row["email"],
                "created_at": row["created_at"]
            }

    except sqlite3.Error:
        # Log the real error internally in a real application.
        # Do not expose database errors to users.
        raise RuntimeError("Database query failed")