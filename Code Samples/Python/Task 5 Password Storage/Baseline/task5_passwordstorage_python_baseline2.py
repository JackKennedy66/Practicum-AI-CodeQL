import bcrypt

def store_password(username, password, db):
    # Convert password to bytes
    password_bytes = password.encode("utf-8")
    
    # Generate a salt and hash the password
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    # Store username + hashed password in your database (dict, file, SQL, etc.)
    db[username] = hashed
    return hashed

# Example usage:
database = {}
store_password("alice", "MySecurePassword123!", database)
print(database)
