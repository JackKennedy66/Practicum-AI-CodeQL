import subprocess

ALLOWED_COMMANDS = {
    "date": ["date"],
    "whoami": ["whoami"],
    "list": ["dir"]  # Windows command
}

def run_command(user_input):
    command = user_input.strip().lower()

    if command not in ALLOWED_COMMANDS:
        return "Error: Command not allowed."

    try:
        result = subprocess.run(
            ALLOWED_COMMANDS[command],
            capture_output=True,
            text=True,
            shell=True,
            timeout=5
        )
        return result.stdout or result.stderr

    except subprocess.TimeoutExpired:
        return "Error: Command timed out."

def main():
    print("Available commands: date, whoami, list")

    while True:
        user_input = input("Enter command or 'exit': ")

        if user_input.lower() == "exit":
            break

        output = run_command(user_input)
        print(output)

if __name__ == "__main__":
    main()