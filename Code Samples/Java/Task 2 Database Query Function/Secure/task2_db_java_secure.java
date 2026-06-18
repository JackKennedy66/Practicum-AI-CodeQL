import java.sql.*;
import java.util.Optional;
import java.util.regex.Pattern;

public class UserRepository {

    private static final Pattern USERNAME_PATTERN =
            Pattern.compile("^[a-zA-Z0-9_]{3,30}$");

    public Optional<User> getUserByUsername(Connection connection, String username)
            throws SQLException {

        if (username == null || !USERNAME_PATTERN.matcher(username).matches()) {
            throw new IllegalArgumentException("Invalid username format");
        }

        String sql = """
            SELECT id, username, email
            FROM users
            WHERE username = ?
            """;

        try (PreparedStatement statement = connection.prepareStatement(sql)) {
            statement.setString(1, username);

            try (ResultSet resultSet = statement.executeQuery()) {
                if (resultSet.next()) {
                    User user = new User(
                            resultSet.getInt("id"),
                            resultSet.getString("username"),
                            resultSet.getString("email")
                    );

                    return Optional.of(user);
                }
            }
        }

        return Optional.empty();
    }
}