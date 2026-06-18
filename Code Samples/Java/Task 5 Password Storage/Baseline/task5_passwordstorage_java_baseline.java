import java.util.HashMap;
import java.util.Map;

public class UserManager {

    private Map<String, String> users = new HashMap<>();

    public void storePassword(String username, String password) {
        users.put(username, password);
    }

    public String getPassword(String username) {
        return users.get(username);
    }

    public static void main(String[] args) {
        UserManager manager = new UserManager();

        manager.storePassword("john", "mypassword123");

        System.out.println("Stored password: " +
                manager.getPassword("john"));
    }
}