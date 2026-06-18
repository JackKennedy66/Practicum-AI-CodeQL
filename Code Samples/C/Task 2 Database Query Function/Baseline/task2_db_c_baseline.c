#include <stdio.h>
#include <sqlite3.h>

void getUserByUsername(sqlite3 *db, const char *username) {
    sqlite3_stmt *stmt;
    const char *sql =
        "SELECT id, username, email FROM users WHERE username = ?";

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        fprintf(stderr, "Failed to prepare statement: %s\n",
                sqlite3_errmsg(db));
        return;
    }

    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_STATIC);

    int rc = sqlite3_step(stmt);

    if (rc == SQLITE_ROW) {
        int id = sqlite3_column_int(stmt, 0);
        const unsigned char *user = sqlite3_column_text(stmt, 1);
        const unsigned char *email = sqlite3_column_text(stmt, 2);

        printf("ID: %d\n", id);
        printf("Username: %s\n", user);
        printf("Email: %s\n", email);
    } else {
        printf("User not found.\n");
    }

    sqlite3_finalize(stmt);
}