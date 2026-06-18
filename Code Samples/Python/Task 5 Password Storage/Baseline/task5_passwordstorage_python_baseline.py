import bcrypt

def hash_password(password: str) -> str:
    """
    Hash a user password using bcrypt.
    """
    if not isinstance(password, str) or not password:
        raise ValueError("Password must be a non-empty string")

    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password_bytes, salt)

    return hashed.decode("utf-8")


def verify_password(password: str, stored_hash: str) -> bool:
    """
    Verify a password against a stored bcrypt hash.
    """
    if not password or not stored_hash:
        return False

    return bcrypt.checkpw(
        password.encode("utf-8"),
        stored_hash.encode("utf-8")
    )


# Example usage
hashed_password = hash_password("MySecurePassword123!")
print("Stored hash:", hashed_password)

if verify_password("MySecurePassword123!", hashed_password):
    print("Password is valid")
else:
    print("Invalid password")