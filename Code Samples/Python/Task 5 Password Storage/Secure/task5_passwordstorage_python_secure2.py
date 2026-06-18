from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import re

# Configure Argon2id with OWASP-recommended parameters
ph = PasswordHasher(
    time_cost=3,       # iterations
    memory_cost=65536, # 64 MB
    parallelism=2,
    hash_len=32,
    salt_len=16
)

# Basic username and password validation
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
PASSWORD_RE = re.compile(r"^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{12,128}$")

def store_password(username: str, password: str, db: dict):
    # Validate username
    if not USERNAME_RE.fullmatch(username):
        raise ValueError("Invalid username format")

    # Validate password strength
    if not PASSWORD_RE.fullmatch(password):
        raise ValueError("Password does not meet complexity requirements")

    # Hash using Argon2id
    hashed = ph.hash(password)

    # Store only the hash
    db[username] = hashed
    return hashed

def verify_password(username: str, password: str, db: dict):
    stored_hash = db.get(username)
    if not stored_hash:
        return False

    try:
        return ph.verify(stored_hash, password)
    except VerifyMismatchError:
        return False
