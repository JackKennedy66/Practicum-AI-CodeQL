#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <sqlite3.h>

#define MAX_USERNAME 32

int is_valid_username(const char *username) {
    size_t len = strlen(username);

    if (len == 0 || len > MAX_USERNAME) {
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

int main(void) {
    sqlite3 *db = NULL;
    sqlite3_stmt *stmt = NULL;
    char username[MAX_USERNAME + 2];

    if (sqlite3_open("users.db", &db) != SQLITE_OK) {
        fprintf(stderr, "Database error.\n");
        return 1;
    }

    printf("Enter username to search: ");

    if (fgets(username, sizeof(username), stdin) == NULL) {
        fprintf(stderr, "Input error.\n");
        sqlite3_close(db);
        return 1;
    }

    username[strcspn(username, "\n")] = '\0';

    if (!is_valid_username(username)) {
        fprintf(stderr, "Invalid username. Use only letters, numbers, underscores, or hyphens.\n");
        sqlite3_close(db);
        return 1;
    }

    const char *sql =
        "SELECT id, username, email "
        "FROM users "
        "WHERE username = ? "
        "LIMIT 1;";

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        fprintf(stderr, "Query preparation failed.\n");
        sqlite3_close(db);
        return 1;
    }

    if (sqlite3_bind_text(stmt, 1, username, -1, SQLITE_TRANSIENT) != SQLITE_OK) {
        fprintf(stderr, "Query binding failed.\n");
        sqlite3_finalize(stmt);
        sqlite3_close(db);
        return 1;
    }

    int result = sqlite3_step(stmt);

    if (result == SQLITE_ROW) {
        int id = sqlite3_column_int(stmt, 0);
        const unsigned char *db_username = sqlite3_column_text(stmt, 1);
        const unsigned char *email = sqlite3_column_text(stmt, 2);

        printf("\nUser found:\n");
        printf("ID: %d\n", id);
        printf("Username: %s\n", db_username ? (const char *)db_username : "");
        printf("Email: %s\n", email ? (const char *)email : "");
    } else if (result == SQLITE_DONE) {
        printf("No user found with that username.\n");
    } else {
        fprintf(stderr, "Search failed.\n");
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);

    return 0;
}