#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sqlite3.h>

#define MAX_USERNAME 100

int main() {
    sqlite3 *db;
    sqlite3_stmt *stmt;
    char username[MAX_USERNAME];

    if (sqlite3_open("users.db", &db) != SQLITE_OK) {
        printf("Could not open database: %s\n", sqlite3_errmsg(db));
        return 1;
    }

    printf("Enter username to search: ");
    fgets(username, sizeof(username), stdin);
    username[strcspn(username, "\n")] = '\0';

    const char *sql = "SELECT id, username, email FROM users WHERE username = ?";

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        printf("SQL error: %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        return 1;
    }

    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_STATIC);

    printf("\nSearch results:\n");

    int found = 0;

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        found = 1;
        printf("ID: %d\n", sqlite3_column_int(stmt, 0));
        printf("Username: %s\n", sqlite3_column_text(stmt, 1));
        printf("Email: %s\n\n", sqlite3_column_text(stmt, 2));
    }

    if (!found) {
        printf("No user found with that username.\n");
    }

    sqlite3_finalize(stmt);
    sqlite3_close(db);

    return 0;
}