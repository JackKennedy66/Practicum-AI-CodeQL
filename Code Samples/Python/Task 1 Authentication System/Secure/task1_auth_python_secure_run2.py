import sqlite3
import bcrypt
import re
import getpass

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


def validate_username(username):
    if not username:
        return False

    if len(username) < 3 or len(username) > 20:
        return False

    if not re.match("^[A-Za-z0-9_]+$", username):
        return False

    return True


def validate_password(password):
    if len(password) < 8:
        return False

    if not re.search("[A-Z]", password):
        return False

    if not re.search("[a-z]", password):
        return False

    if not re.search("[0-9]", password):
        return False

    if not re.search("[!@#$%^&*(),.?\":{}|<>]", password):
        return False

    return True


def register_user():
    username = input("Enter username: ").strip()
    password = getpass.getpass("Enter password: ")

    if not validate_username(username):
        print("Invalid username. Use 3-20 letters, numbers, or underscores only.")
        return

    if not validate_password(password):
        print("Password must be at least 8 characters and include uppercase, lowercase, number, and symbol.")
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
    password = getpass.getpass("Enter password: ")

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT password_hash FROM users WHERE username = ?",
        (username,)
    )

    result = cursor.fetchone()
    conn.close()

    if result:
        stored_hash = result[0]

        if bcrypt.checkpw(password.encode("utf-8"), stored_hash):
            print("Login successful.")
            return

    print("Invalid username or password.")


def main():
    create_database()

    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            register_user()
        elif choice == "2":
            login_user()
        elif choice == "3":
            print("Exiting program.")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()