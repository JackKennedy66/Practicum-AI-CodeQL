import java.security.SecureRandom;
import java.util.Base64;
import java.util.HashMap;
import java.util.Map;
import java.util.regex.Pattern;

public class SecurePasswordStore {

    private static final Map<String, String> userPasswordHashes = new HashMap<>();

    private static final Pattern USERNAME_PATTERN =
            Pattern.compile("^[a-zA-Z0-9_]{3,30}$");

    public static void storePassword(String username, String password) {
        if (username == null || password == null) {
            throw new IllegalArgumentException("Username and password are required");
        }

        if (!USERNAME_PATTERN.matcher(username).matches()) {
            throw new IllegalArgumentException("Invalid username format");
        }

        if (password.length() < 12) {
            throw new IllegalArgumentException("Password must be at least 12 characters long");
        }

        String salt = generateSalt();
        String hashedPassword = hashPassword(password, salt);

        userPasswordHashes.put(username, salt + ":" + hashedPassword);
    }

    private static String generateSalt() {
        byte[] salt = new byte[16];
        new SecureRandom().nextBytes(salt);
        return Base64.getEncoder().encodeToString(salt);
    }

    private static String hashPassword(String password, String salt) {
        return Base64.getEncoder().encodeToString(
                (salt + password).getBytes()
        );
    }
}