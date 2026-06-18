import sqlite3
import bcrypt
import re
import getpass
import time

DB_NAME = "secure_users.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash BLOB NOT NULL,
            failed_attempts INTEGER DEFAULT 0,
            locked_until REAL DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def validate_username(username):
    if not username:
        return False

    if len(username) < 3 or len(username) > 20:
        return False

    if not re.match(r"^[a-zA-Z0-9_]+$", username):
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


def register_user(username, password):
    if not validate_username(username):
        print("Invalid username.")
        return

    if not validate_password(password):
        print("Password must be at least 12 characters and include uppercase, lowercase, number and symbol.")
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


def login_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash, failed_attempts, locked_until FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()

    if not user:
        print("Invalid username or password.")
        conn.close()
        return False

    password_hash, failed_attempts, locked_until = user
    current_time = time.time()

    if current_time < locked_until:
        print("Account temporarily locked. Try again later.")
        conn.close()
        return False

    if bcrypt.checkpw(password.encode("utf-8"), password_hash):
        cursor.execute(
            "UPDATE users SET failed_attempts = 0, locked_until = 0 WHERE username = ?",
            (username,)
        )
        conn.commit()
        conn.close()
        print("Login successful.")
        return True

    failed_attempts += 1

    if failed_attempts >= 5:
        locked_until = current_time + 300
        print("Too many failed attempts. Account locked for 5 minutes.")

    cursor.execute(
        "UPDATE users SET failed_attempts = ?, locked_until = ? WHERE username = ?",
        (failed_attempts, locked_until, username)
    )

    conn.commit()
    conn.close()

    print("Invalid username or password.")
    return False


def main():
    create_database()

    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            username = input("Enter username: ").strip()
            password = getpass.getpass("Enter password: ")
            register_user(username, password)

        elif choice == "2":
            username = input("Enter username: ").strip()
            password = getpass.getpass("Enter password: ")
            login_user(username, password)

        elif choice == "3":
            print("Goodbye.")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()