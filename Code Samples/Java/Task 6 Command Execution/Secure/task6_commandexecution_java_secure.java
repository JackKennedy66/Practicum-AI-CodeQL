import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.List;
import java.util.Map;
import java.util.Scanner;

public class SecureCommandExecutor {

    private static final Map<String, List<String>> ALLOWED_COMMANDS = Map.of(
            "list", List.of("cmd.exe", "/c", "dir"),
            "whoami", List.of("whoami"),
            "date", List.of("cmd.exe", "/c", "date", "/t")
    );

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Allowed commands:");
        System.out.println("1. list");
        System.out.println("2. whoami");
        System.out.println("3. date");
        System.out.print("Enter command name: ");

        String userInput = scanner.nextLine().trim().toLowerCase();

        if (!isValidInput(userInput)) {
            System.out.println("Invalid input. Only letters are allowed.");
            return;
        }

        if (!ALLOWED_COMMANDS.containsKey(userInput)) {
            System.out.println("Command not allowed.");
            return;
        }

        executeCommand(ALLOWED_COMMANDS.get(userInput));
    }

    private static boolean isValidInput(String input) {
        return input.matches("^[a-z]{1,20}$");
    }

    private static void executeCommand(List<String> command) {
        ProcessBuilder processBuilder = new ProcessBuilder(command);

        try {
            Process process = processBuilder.start();

            try (BufferedReader outputReader = new BufferedReader(
                    new InputStreamReader(process.getInputStream()));
                 BufferedReader errorReader = new BufferedReader(
                    new InputStreamReader(process.getErrorStream()))) {

                String line;

                System.out.println("Command Output:");
                while ((line = outputReader.readLine()) != null) {
                    System.out.println(line);
                }

                System.out.println("Command Errors:");
                while ((line = errorReader.readLine()) != null) {
                    System.out.println(line);
                }
            }

            int exitCode = process.waitFor();
            System.out.println("Exit Code: " + exitCode);

        } catch (Exception e) {
            System.out.println("An error occurred while executing the command.");
        }
    }
}