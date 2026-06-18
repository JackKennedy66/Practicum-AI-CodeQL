import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.Statement;

public class UserRepository {

    public User getUserByUsername(String username) {
        User user = null;

        try {
            Connection conn = DriverManager.getConnection(
                "jdbc:mysql://localhost:3306/mydb",
                "root",
                "password"
            );

            Statement stmt = conn.createStatement();

            String query = "SELECT id, username, email FROM users WHERE username = '"
                    + username + "'";

            ResultSet rs = stmt.executeQuery(query);

            if (rs.next()) {
                user = new User(
                    rs.getInt("id"),
                    rs.getString("username"),
                    rs.getString("email")
                );
            }

            rs.close();
            stmt.close();
            conn.close();

        } catch (Exception e) {
            e.printStackTrace();
        }

        return user;
    }
}