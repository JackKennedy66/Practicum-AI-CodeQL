# secure_auth_system.py

import sqlite3
import bcrypt
import re
import getpass
import time
from datetime import datetime, timedelta

DB_NAME = "secure_users.db"

MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_TIME_MINUTES = 5


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            failed_attempts INTEGER DEFAULT 0,
            lockout_until TEXT
        )
    """)

    conn.commit()
    conn.close()


def validate_username(username):
    if not username:
        return False

    if len(username) < 3 or len(username) > 30:
        return False

    if not re.match(r"^[A-Za-z0-9_]+$", username):
        return False

    return True


def validate_password(password):
    if len(password) < 12:
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
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())


def register_user(username, password):
    username = username.strip()

    if not validate_username(username):
        print("Invalid username. Use 3–30 letters, numbers, or underscores only.")
        return

    if not validate_password(password):
        print("Password must be at least 12 characters and include uppercase, lowercase, number, and special character.")
        return

    password_hash = hash_password(password)

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash)
        )
        conn.commit()
        print("User registered successfully.")

    except sqlite3.IntegrityError:
        print("Username already exists.")

    finally:
        conn.close()


def is_account_locked(lockout_until):
    if lockout_until is None:
        return False

    lockout_time = datetime.fromisoformat(lockout_until)
    return datetime.now() < lockout_time


def login_user(username, password):
    username = username.strip()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id, password_hash, failed_attempts, lockout_until FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    if user is None:
        time.sleep(1)
        print("Invalid username or password.")
        conn.close()
        return False

    user_id, stored_hash, failed_attempts, lockout_until = user

    if is_account_locked(lockout_until):
        print("Account is temporarily locked. Please try again later.")
        conn.close()
        return False

    if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
        cursor.execute(
            "UPDATE users SET failed_attempts = 0, lockout_until = NULL WHERE id = ?",
            (user_id,)
        )
        conn.commit()
        conn.close()
        print("Login successful.")
        return True

    failed_attempts += 1

    if failed_attempts >= MAX_LOGIN_ATTEMPTS:
        lockout_time = datetime.now() + timedelta(minutes=LOCKOUT_TIME_MINUTES)
        cursor.execute(
            "UPDATE users SET failed_attempts = ?, lockout_until = ? WHERE id = ?",
            (failed_attempts, lockout_time.isoformat(), user_id)
        )
        print("Too many failed attempts. Account locked temporarily.")
    else:
        cursor.execute(
            "UPDATE users SET failed_attempts = ? WHERE id = ?",
            (failed_attempts, user_id)
        )
        print("Invalid username or password.")

    conn.commit()
    conn.close()
    return False


def main():
    create_database()

    while True:
        print("\nSecure User Authentication System")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            username = input("Enter username: ")
            password = getpass.getpass("Enter password: ")
            register_user(username, password)

        elif choice == "2":
            username = input("Enter username: ")
            password = getpass.getpass("Enter password: ")
            login_user(username, password)

        elif choice == "3":
            print("Goodbye.")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()