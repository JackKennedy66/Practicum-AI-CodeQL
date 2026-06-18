import subprocess
import re
import logging

logging.basicConfig(
    filename="command_app.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

ALLOWED_COMMANDS = {
    "date": ["date"],
    "whoami": ["whoami"],
    "list": ["dir"]  # Windows
}

VALID_INPUT_PATTERN = re.compile(r"^[a-zA-Z]+$")

def validate_input(user_input):
    if not user_input:
        raise ValueError("Input cannot be empty.")

    if len(user_input) > 20:
        raise ValueError("Input is too long.")

    if not VALID_INPUT_PATTERN.match(user_input):
        raise ValueError("Input contains invalid characters.")

    return user_input.lower()

def execute_command(command_name):
    if command_name not in ALLOWED_COMMANDS:
        raise ValueError("Command is not allowed.")

    try:
        result = subprocess.run(
            ALLOWED_COMMANDS[command_name],
            capture_output=True,
            text=True,
            shell=False,
            timeout=5,
            check=False
        )

        logging.info("Executed allowed command: %s", command_name)

        if result.returncode != 0:
            return "Command failed to execute safely."

        return result.stdout.strip() or "Command executed successfully."

    except subprocess.TimeoutExpired:
        logging.warning("Command timed out: %s", command_name)
        return "Command timed out."
    except Exception:
        logging.exception("Unexpected error during command execution")
        return "An error occurred while executing the command."

def main():
    print("Secure Command Execution Application")
    print("Allowed commands: date, whoami, list")
    print("Type 'exit' to quit.")

    while True:
        try:
            user_input = input("Enter command: ").strip()

            if user_input.lower() == "exit":
                print("Goodbye.")
                break

            command_name = validate_input(user_input)
            output = execute_command(command_name)
            print(output)

        except ValueError as error:
            print(f"Invalid input: {error}")

if __name__ == "__main__":
    main()