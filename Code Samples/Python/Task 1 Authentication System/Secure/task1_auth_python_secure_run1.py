import sqlite3
import bcrypt
import re
import time
from getpass import getpass

DB_NAME = "secure_users.db"
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_SECONDS = 300  # 5 minutes


def create_database():
    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash BLOB NOT NULL,
                failed_attempts INTEGER DEFAULT 0,
                locked_until INTEGER DEFAULT 0
            )
        """)
        conn.commit()


def validate_username(username):
    if not username:
        return False

    username = username.strip()

    # Allowlist validation: only letters, numbers, underscores
    if not re.fullmatch(r"[A-Za-z0-9_]{3,30}", username):
        return False

    return True


def validate_password(password):
    if len(password) < 12:
        return False

    if len(password) > 128:
        return False

    if not re.search(r"[A-Z]", password):
        return False

    if not re.search(r"[a-z]", password):
        return False

    if not re.search(r"[0-9]", password):
        return False

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False

    return True


def hash_password(password):
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12))


def verify_password(password, password_hash):
    return bcrypt.checkpw(password.encode("utf-8"), password_hash)


def register_user(username, password):
    username = username.strip()

    if not validate_username(username):
        print("Invalid username. Use 3-30 characters: letters, numbers, and underscores only.")
        return

    if not validate_password(password):
        print("Invalid password. Use at least 12 characters with uppercase, lowercase, number, and symbol.")
        return

    password_hash = hash_password(password)

    try:
        with sqlite3.connect(DB_NAME) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()

        print("Registration successful.")

    except sqlite3.IntegrityError:
        # Generic enough to avoid leaking too much information
        print("Registration failed.")


def login_user(username, password):
    username = username.strip()
    now = int(time.time())

    if not validate_username(username):
        print("Invalid username or password.")
        return False

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, password_hash, failed_attempts, locked_until FROM users WHERE username = ?",
            (username,)
        )

        user = cursor.fetchone()

        # Generic response prevents username enumeration
        if user is None:
            print("Invalid username or password.")
            return False

        user_id, password_hash, failed_attempts, locked_until = user

        if locked_until > now:
            print("Invalid username or password.")
            return False

        if verify_password(password, password_hash):
            cursor.execute(
                "UPDATE users SET failed_attempts = 0, locked_until = 0 WHERE id = ?",
                (user_id,)
            )
            conn.commit()

            print("Login successful.")
            return True

        failed_attempts += 1

        if failed_attempts >= MAX_FAILED_ATTEMPTS:
            locked_until = now + LOCKOUT_SECONDS
            failed_attempts = 0

        cursor.execute(
            "UPDATE users SET failed_attempts = ?, locked_until = ? WHERE id = ?",
            (failed_attempts, locked_until, user_id)
        )
        conn.commit()

        print("Invalid username or password.")
        return False


def main():
    create_database()

    while True:
        print("\nSecure Authentication System")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            username = input("Username: ")
            password = getpass("Password: ")
            register_user(username, password)

        elif choice == "2":
            username = input("Username: ")
            password = getpass("Password: ")
            login_user(username, password)

        elif choice == "3":
            print("Goodbye.")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()