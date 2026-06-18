import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.util.Scanner;

public class CommandExecutor {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("Enter a system command to execute:");
        String command = scanner.nextLine();

        try {
            Process process = Runtime.getRuntime().exec(command);

            BufferedReader outputReader = new BufferedReader(
                    new InputStreamReader(process.getInputStream())
            );

            BufferedReader errorReader = new BufferedReader(
                    new InputStreamReader(process.getErrorStream())
            );

            String line;

            System.out.println("Command Output:");
            while ((line = outputReader.readLine()) != null) {
                System.out.println(line);
            }

            System.out.println("Command Errors:");
            while ((line = errorReader.readLine()) != null) {
                System.out.println(line);
            }

            process.waitFor();

        } catch (Exception e) {
            System.out.println("Error executing command: " + e.getMessage());
        }

        scanner.close();
    }
}