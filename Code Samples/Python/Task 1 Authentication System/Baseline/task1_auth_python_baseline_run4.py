import sqlite3
import hashlib
import os

DB_NAME = "users.db"


def create_database():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password, salt):
    return hashlib.sha256((password + salt).encode()).hexdigest()


def register_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    salt = os.urandom(16).hex()
    password_hash = hash_password(password, salt)

    try:
        cursor.execute(
            "INSERT INTO users (username, password_hash, salt) VALUES (?, ?, ?)",
            (username, password_hash, salt)
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
        "SELECT password_hash, salt FROM users WHERE username = ?",
        (username,)
    )

    user = cursor.fetchone()
    conn.close()

    if user:
        stored_hash, salt = user
        if hash_password(password, salt) == stored_hash:
            print("Login successful.")
            return True

    print("Invalid username or password.")
    return False


def main():
    create_database()

    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            username = input("Enter username: ")
            password = input("Enter password: ")
            register_user(username, password)

        elif choice == "2":
            username = input("Enter username: ")
            password = input("Enter password: ")
            login_user(username, password)

        elif choice == "3":
            print("Goodbye.")
            break

        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()