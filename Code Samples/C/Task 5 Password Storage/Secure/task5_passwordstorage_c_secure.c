#include <sodium.h>
#include <sqlite3.h>
#include <string.h>
#include <ctype.h>

#define MAX_USERNAME_LEN 64
#define MIN_PASSWORD_LEN 12
#define MAX_PASSWORD_LEN 256

int is_valid_username(const char *username) {
    size_t len;

    if (username == NULL) return 0;

    len = strlen(username);
    if (len == 0 || len > MAX_USERNAME_LEN) return 0;

    for (size_t i = 0; i < len; i++) {
        if (!isalnum((unsigned char)username[i]) &&
            username[i] != '_' &&
            username[i] != '-') {
            return 0;
        }
    }

    return 1;
}

int is_valid_password(const char *password) {
    size_t len;

    if (password == NULL) return 0;

    len = strlen(password);
    if (len < MIN_PASSWORD_LEN || len > MAX_PASSWORD_LEN) {
        return 0;
    }

    return 1;
}

int store_user_password(sqlite3 *db, const char *username, const char *password) {
    sqlite3_stmt *stmt = NULL;
    char password_hash[crypto_pwhash_STRBYTES];
    const char *sql =
        "INSERT INTO users (username, password_hash) VALUES (?, ?);";

    if (db == NULL || !is_valid_username(username) || !is_valid_password(password)) {
        return -1;
    }

    if (sodium_init() < 0) {
        return -1;
    }

    if (crypto_pwhash_str(
            password_hash,
            password,
            strlen(password),
            crypto_pwhash_OPSLIMIT_INTERACTIVE,
            crypto_pwhash_MEMLIMIT_INTERACTIVE) != 0) {
        return -1;
    }

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        sodium_memzero(password_hash, sizeof(password_hash));
        return -1;
    }

    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, password_hash, -1, SQLITE_TRANSIENT);

    int result = sqlite3_step(stmt);

    sqlite3_finalize(stmt);
    sodium_memzero(password_hash, sizeof(password_hash));

    if (result != SQLITE_DONE) {
        return -1;
    }

    return 0;
}