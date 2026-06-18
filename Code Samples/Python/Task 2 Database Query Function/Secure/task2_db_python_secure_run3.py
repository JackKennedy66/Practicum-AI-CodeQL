import re
import sqlite3
from typing import Optional, Dict, Any


USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]{3,30}$")


def get_user_by_username(db_path: str, username: str) -> Optional[Dict[str, Any]]:
    """
    Securely retrieves a user record by username.

    Returns:
        A dictionary containing the user record, or None if no user is found.
    """

    if not isinstance(username, str):
        raise ValueError("Username must be a string")

    username = username.strip()

    if not USERNAME_PATTERN.fullmatch(username):
        raise ValueError(
            "Invalid username. Usernames must be 3-30 characters and contain only "
            "letters, numbers, underscores, dots, or hyphens."
        )

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

            return dict(row)

    except sqlite3.Error:
        raise RuntimeError("Database error occurred")