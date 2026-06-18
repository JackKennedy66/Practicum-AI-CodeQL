#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <sqlite3.h>

#define MAX_USERNAME_LEN 50

typedef struct {
    int id;
    char username[MAX_USERNAME_LEN + 1];
    char email[255];
} User;

int is_valid_username(const char *username) {
    if (username == NULL) {
        return 0;
    }

    size_t len = strlen(username);

    if (len == 0 || len > MAX_USERNAME_LEN) {
        return 0;
    }

    for (size_t i = 0; i < len; i++) {
        if (!isalnum((unsigned char)username[i]) &&
            username[i] != '_' &&
            username[i] != '-') {
            return 0;
        }
    }

    return 1;
}

int get_user_by_username(sqlite3 *db, const char *username, User *user) {
    sqlite3_stmt *stmt = NULL;

    const char *sql =
        "SELECT id, username, email "
        "FROM users "
        "WHERE username = ? "
        "LIMIT 1";

    if (db == NULL || user == NULL) {
        return -1;
    }

    if (!is_valid_username(username)) {
        return -2;
    }

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return -3;
    }

    if (sqlite3_bind_text(stmt, 1, username, -1, SQLITE_TRANSIENT) != SQLITE_OK) {
        sqlite3_finalize(stmt);
        return -4;
    }

    int rc = sqlite3_step(stmt);

    if (rc == SQLITE_ROW) {
        user->id = sqlite3_column_int(stmt, 0);

        const unsigned char *db_username = sqlite3_column_text(stmt, 1);
        const unsigned char *db_email = sqlite3_column_text(stmt, 2);

        if (db_username == NULL || db_email == NULL) {
            sqlite3_finalize(stmt);
            return -5;
        }

        snprintf(user->username, sizeof(user->username), "%s", db_username);
        snprintf(user->email, sizeof(user->email), "%s", db_email);

        sqlite3_finalize(stmt);
        return 1;
    }

    sqlite3_finalize(stmt);

    if (rc == SQLITE_DONE) {
        return 0;
    }

    return -6;
}