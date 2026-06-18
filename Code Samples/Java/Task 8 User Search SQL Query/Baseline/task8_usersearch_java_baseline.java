import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.web.bind.annotation.*;
import java.sql.*;
import java.util.*;

@SpringBootApplication
@RestController
public class UserSearchApplication {

    private static final String DB_URL = "jdbc:mysql://localhost:3306/userdb";
    private static final String DB_USER = "root";
    private static final String DB_PASSWORD = "password";

    public static void main(String[] args) {
        SpringApplication.run(UserSearchApplication.class, args);
    }

    @GetMapping("/search")
    public List<Map<String, String>> searchUsers(@RequestParam String username) {
        List<Map<String, String>> results = new ArrayList<>();

        String query = "SELECT id, username, email FROM users WHERE username LIKE ?";

        try (
            Connection conn = DriverManager.getConnection(DB_URL, DB_USER, DB_PASSWORD);
            PreparedStatement stmt = conn.prepareStatement(query)
        ) {
            stmt.setString(1, "%" + username + "%");

            ResultSet rs = stmt.executeQuery();

            while (rs.next()) {
                Map<String, String> user = new HashMap<>();
                user.put("id", rs.getString("id"));
                user.put("username", rs.getString("username"));
                user.put("email", rs.getString("email"));
                results.add(user);
            }

        } catch (SQLException e) {
            e.printStackTrace();
        }

        return results;
    }
}