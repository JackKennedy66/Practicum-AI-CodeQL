import java.security.NoSuchAlgorithmException;
import java.security.SecureRandom;
import java.security.spec.InvalidKeySpecException;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;
import java.util.regex.Pattern;

import javax.crypto.SecretKeyFactory;
import javax.crypto.spec.PBEKeySpec;

public class SecureUserAuthentication {

    private static final Map<String, UserRecord> users = new HashMap<>();

    private static final int SALT_LENGTH = 16;
    private static final int ITERATIONS = 120_000;
    private static final int KEY_LENGTH = 256;

    private static final Pattern USERNAME_PATTERN =
            Pattern.compile("^[a-zA-Z0-9_]{3,20}$");

    static class UserRecord {
        private final String salt;
        private final String passwordHash;

        UserRecord(String salt, String passwordHash) {
            this.salt = salt;
            this.passwordHash = passwordHash;
        }
    }

    public static boolean isValidUsername(String username) {
        return username != null && USERNAME_PATTERN.matcher(username).matches();
    }

    public static boolean isValidPassword(String password) {
        return password != null
                && password.length() >= 12
                && password.matches(".*[A-Z].*")
                && password.matches(".*[a-z].*")
                && password.matches(".*\\d.*")
                && password.matches(".*[^a-zA-Z0-9].*");
    }

    public static void registerUser(String username, String password)
            throws NoSuchAlgorithmException, InvalidKeySpecException {

        if (!isValidUsername(username)) {
            throw new IllegalArgumentException(
                    "Username must be 3-20 characters and contain only letters, numbers, or underscores."
            );
        }

        if (!isValidPassword(password)) {
            throw new IllegalArgumentException(
                    "Password must be at least 12 characters and include uppercase, lowercase, number, and special character."
            );
        }

        if (users.containsKey(username)) {
            throw new IllegalArgumentException("Username already exists.");
        }

        byte[] salt = generateSalt();
        String passwordHash = hashPassword(password.toCharArray(), salt);

        users.put(username, new UserRecord(
                Base64.getEncoder().encodeToString(salt),
                passwordHash
        ));

        System.out.println("User registered successfully.");
    }

    public static boolean loginUser(String username, String password)
            throws NoSuchAlgorithmException, InvalidKeySpecException {

        if (!isValidUsername(username) || password == null) {
            return false;
        }

        UserRecord record = users.get(username);

        if (record == null) {
            return false;
        }

        byte[] salt = Base64.getDecoder().decode(record.salt);
        String attemptedHash = hashPassword(password.toCharArray(), salt);

        return constantTimeEquals(record.passwordHash, attemptedHash);
    }

    private static byte[] generateSalt() {
        byte[] salt = new byte[SALT_LENGTH];
        new SecureRandom().nextBytes(salt);
        return salt;
    }

    private static String hashPassword(char[] password, byte[] salt)
            throws NoSuchAlgorithmException, InvalidKeySpecException {

        PBEKeySpec spec = new PBEKeySpec(password, salt, ITERATIONS, KEY_LENGTH);
        SecretKeyFactory factory = SecretKeyFactory.getInstance("PBKDF2WithHmacSHA256");

        byte[] hash = factory.generateSecret(spec).getEncoded();
        spec.clearPassword();

        return Base64.getEncoder().encodeToString(hash);
    }

    private static boolean constantTimeEquals(String storedHash, String attemptedHash) {
        byte[] a = storedHash.getBytes();
        byte[] b = attemptedHash.getBytes();

        if (a.length != b.length) {
            return false;
        }

        int result = 0;

        for (int i = 0; i < a.length; i++) {
            result |= a[i] ^ b[i];
        }

        return result == 0;
    }

    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        try {
            System.out.println("=== Secure User Authentication System ===");

            System.out.print("Create username: ");
            String username = scanner.nextLine().trim();

            System.out.print("Create password: ");
            String password = scanner.nextLine();

            registerUser(username, password);

            System.out.println("\n=== Login ===");

            System.out.print("Enter username: ");
            String loginUsername = scanner.nextLine().trim();

            System.out.print("Enter password: ");
            String loginPassword = scanner.nextLine();

            if (loginUser(loginUsername, loginPassword)) {
                System.out.println("Login successful.");
            } else {
                System.out.println("Invalid username or password.");
            }

        } catch (IllegalArgumentException e) {
            System.out.println("Input error: " + e.getMessage());
        } catch (Exception e) {
            System.out.println("Authentication error occurred.");
        } finally {
            scanner.close();
        }
    }
}