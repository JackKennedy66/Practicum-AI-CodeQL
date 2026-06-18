import sqlite3
import bcrypt
import re
from getpass import getpass

DB_NAME = "secure_users.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def is_valid_username(username):
    return re.match(r"^[A-Za-z0-9_]{3,20}$", username) is not None


def is_valid_password(password):
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


def register_user():
    username = input("Enter username: ").strip()
    password = getpass("Enter password: ")

    if not is_valid_username(username):
        print("Invalid username. Use 3-20 letters, numbers, or underscores only.")
        return

    if not is_valid_password(password):
        print("Password must be 8+ characters and include uppercase, lowercase, number, and symbol.")
        return

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    try:
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()

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


def login_user():
    username = input("Enter username: ").strip()
    password = getpass("Enter password: ")

    if not is_valid_username(username):
        print("Invalid username or password.")
        return

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.checkpw(password.encode("utf-8"), user[0]):
        print("Login successful.")
    else:
        print("Invalid username or password.")


def main():
    create_database()

    while True:
        print("\n--- Secure Authentication System ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            login_user()
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main()