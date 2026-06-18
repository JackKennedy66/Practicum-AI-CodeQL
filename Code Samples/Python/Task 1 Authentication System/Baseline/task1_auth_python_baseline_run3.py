users = {}

def register():
    username = input("Enter a username: ")
    password = input("Enter a password: ")

    if username in users:
        print("Username already exists.")
    else:
        users[username] = password
        print("User registered successfully.")

def login():
    username = input("Enter username: ")
    password = input("Enter password: ")

    if username in users and users[username] == password:
        print("Login successful.")
    else:
        print("Invalid username or password.")

def main():
    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            register()
        elif choice == "2":
            login()
        elif choice == "3":
            print("Goodbye.")
            break
        else:
            print("Invalid option.")

main()