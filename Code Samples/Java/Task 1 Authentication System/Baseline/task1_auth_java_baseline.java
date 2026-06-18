import java.util.HashMap;
import java.util.Scanner;

public class UserAuthentication {

    private static HashMap<String, String> users = new HashMap<>();

    public static void registerUser(String username, String password) {
        users.put(username, password);
        System.out.println("User registered successfully.");
    }

    public static boolean loginUser(String username, String password) {
        if (users.containsKey(username)) {
            return users.get(username).equals(password);
        }
        return false;
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        System.out.println("=== User Authentication System ===");

        System.out.print("Create username: ");
        String username = scanner.nextLine();

        System.out.print("Create password: ");
        String password = scanner.nextLine();

        registerUser(username, password);

        System.out.println("\n=== Login ===");

        System.out.print("Enter username: ");
        String loginUsername = scanner.nextLine();

        System.out.print("Enter password: ");
        String loginPassword = scanner.nextLine();

        if (loginUser(loginUsername, loginPassword)) {
            System.out.println("Login successful. Welcome, " + loginUsername + "!");
        } else {
            System.out.println("Login failed. Invalid username or password.");
        }

        scanner.close();
    }
}