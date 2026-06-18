import re
import bcrypt
from typing import Optional


USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,50}$")


def validate_password(password: str) -> None:
    if not isinstance(password, str):
        raise ValueError("Password must be a string")

    if len(password) < 12:
        raise ValueError("Password must be at least 12 characters long")

    if len(password) > 128:
        raise ValueError("Password must not exceed 128 characters")

    if password.strip() != password:
        raise ValueError("Password must not start or end with spaces")

    if "\x00" in password:
        raise ValueError("Password contains invalid characters")


def hash_password(password: str) -> str:
    """
    Securely hashes a password using bcrypt.
    Store only the returned hash in the database.
    Never store the plain-text password.
    """
    validate_password(password)

    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt(rounds=12)
    password_hash = bcrypt.hashpw(password_bytes, salt)

    return password_hash.decode("utf-8")


def store_user_password(db_connection, username: str, password: str) -> None:
    """
    Securely stores a user's password hash using a parameterized query.
    """

    if not isinstance(username, str) or not USERNAME_RE.fullmatch(username):
        raise ValueError("Invalid username format")

    password_hash = hash_password(password)

    query = """
        UPDATE users
        SET password_hash = ?
        WHERE username = ?
    """

    with db_connection:
        db_connection.execute(query, (password_hash, username))


def verify_password(password: str, stored_hash: Optional[str]) -> bool:
    """
    Verifies a plain password against the stored bcrypt hash.
    """

    if not password or not stored_hash:
        return False

    try:
        return bcrypt.checkpw(
            password.encode("utf-8"),
            stored_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False