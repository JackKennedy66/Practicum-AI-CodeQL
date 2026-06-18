/*
 * Secure C REST API for User Management
 *
 * Security improvements:
 * - Uses SQLite prepared statements
 * - Validates user input
 * - Avoids SQL injection
 * - Avoids unsafe sprintf for SQL queries
 * - Uses bounded buffers
 * - Rejects oversized request bodies
 * - Escapes JSON output
 * - Uses proper HTTP status codes
 *
 * Endpoints:
 *   GET    /users
 *   GET    /users?id=1
 *   POST   /users
 *   PUT    /users?id=1
 *   DELETE /users?id=1
 *
 * Compile:
 *   gcc secure_user_api.c -o secure_user_api -lmicrohttpd -lsqlite3
 *
 * Run:
 *   ./secure_user_api
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <sqlite3.h>
#include <microhttpd.h>

#define PORT 8080
#define DB_FILE "users.db"
#define MAX_BODY_SIZE 2048
#define MAX_USERNAME 50
#define MAX_EMAIL 100
#define MAX_ROLE 20
#define MAX_JSON 8192

sqlite3 *db;

struct RequestData {
    char *body;
    size_t size;
};

int send_json(struct MHD_Connection *connection, const char *body, int status) {
    struct MHD_Response *response =
        MHD_create_response_from_buffer(strlen(body), (void *)body, MHD_RESPMEM_MUST_COPY);

    if (!response) {
        return MHD_NO;
    }

    MHD_add_response_header(response, "Content-Type", "application/json");
    MHD_add_response_header(response, "X-Content-Type-Options", "nosniff");
    MHD_add_response_header(response, "Cache-Control", "no-store");

    int ret = MHD_queue_response(connection, status, response);
    MHD_destroy_response(response);

    return ret;
}

int is_valid_id(const char *id) {
    if (!id || strlen(id) == 0 || strlen(id) > 10) {
        return 0;
    }

    for (size_t i = 0; i < strlen(id); i++) {
        if (!isdigit((unsigned char)id[i])) {
            return 0;
        }
    }

    return 1;
}

int is_valid_username(const char *username) {
    size_t len = strlen(username);

    if (len < 3 || len > MAX_USERNAME) {
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

int is_valid_email(const char *email) {
    size_t len = strlen(email);

    if (len < 5 || len > MAX_EMAIL) {
        return 0;
    }

    const char *at = strchr(email, '@');
    const char *dot = strrchr(email, '.');

    if (!at || !dot || at > dot) {
        return 0;
    }

    for (size_t i = 0; i < len; i++) {
        if (isspace((unsigned char)email[i])) {
            return 0;
        }
    }

    return 1;
}

int is_valid_role(const char *role) {
    return strcmp(role, "admin") == 0 ||
           strcmp(role, "manager") == 0 ||
           strcmp(role, "user") == 0;
}

void json_escape(const unsigned char *input, char *output, size_t output_size) {
    size_t j = 0;

    for (size_t i = 0; input[i] != '\0' && j + 2 < output_size; i++) {
        if (input[i] == '"' || input[i] == '\\') {
            if (j + 2 >= output_size) {
                break;
            }

            output[j++] = '\\';
            output[j++] = input[i];
        } else if (input[i] >= 32 && input[i] <= 126) {
            output[j++] = input[i];
        }
    }

    output[j] = '\0';
}

/*
 * Minimal JSON parser for expected format only:
 * {"username":"tara","email":"tara@example.com","role":"user"}
 */
int extract_json_value(const char *json,
                       const char *key,
                       char *out,
                       size_t out_size) {
    char pattern[64];

    if (snprintf(pattern, sizeof(pattern), "\"%s\":\"", key) >= (int)sizeof(pattern)) {
        return 0;
    }

    char *start = strstr(json, pattern);

    if (!start) {
        return 0;
    }

    start += strlen(pattern);

    char *end = strchr(start, '"');

    if (!end) {
        return 0;
    }

    size_t len = end - start;

    if (len == 0 || len >= out_size) {
        return 0;
    }

    memcpy(out, start, len);
    out[len] = '\0';

    return 1;
}

int init_db() {
    const char *sql =
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "username TEXT NOT NULL UNIQUE,"
        "email TEXT NOT NULL UNIQUE,"
        "role TEXT NOT NULL CHECK(role IN ('admin','manager','user')));";

    char *err = NULL;

    if (sqlite3_exec(db, sql, NULL, NULL, &err) != SQLITE_OK) {
        fprintf(stderr, "Database error\n");
        sqlite3_free(err);
        return 0;
    }

    return 1;
}

int handle_get_users(struct MHD_Connection *connection) {
    const char *id = MHD_lookup_connection_value(connection, MHD_GET_ARGUMENT_KIND, "id");

    const char *sql_all =
        "SELECT id, username, email, role FROM users ORDER BY id LIMIT 100;";

    const char *sql_one =
        "SELECT id, username, email, role FROM users WHERE id = ?;";

    sqlite3_stmt *stmt = NULL;

    if (id) {
        if (!is_valid_id(id)) {
            return send_json(connection, "{\"error\":\"Invalid user id\"}", MHD_HTTP_BAD_REQUEST);
        }

        if (sqlite3_prepare_v2(db, sql_one, -1, &stmt, NULL) != SQLITE_OK) {
            return send_json(connection, "{\"error\":\"Database error\"}", MHD_HTTP_INTERNAL_SERVER_ERROR);
        }

        sqlite3_bind_int(stmt, 1, atoi(id));
    } else {
        if (sqlite3_prepare_v2(db, sql_all, -1, &stmt, NULL) != SQLITE_OK) {
            return send_json(connection, "{\"error\":\"Database error\"}", MHD_HTTP_INTERNAL_SERVER_ERROR);
        }
    }

    char json[MAX_JSON];
    size_t offset = 0;

    offset += snprintf(json + offset, sizeof(json) - offset, "[");

    int first = 1;

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        char username[128];
        char email[160];
        char role[64];

        json_escape(sqlite3_column_text(stmt, 1), username, sizeof(username));
        json_escape(sqlite3_column_text(stmt, 2), email, sizeof(email));
        json_escape(sqlite3_column_text(stmt, 3), role, sizeof(role));

        int written = snprintf(json + offset,
                               sizeof(json) - offset,
                               "%s{\"id\":%d,\"username\":\"%s\",\"email\":\"%s\",\"role\":\"%s\"}",
                               first ? "" : ",",
                               sqlite3_column_int(stmt, 0),
                               username,
                               email,
                               role);

        if (written < 0 || written >= (int)(sizeof(json) - offset)) {
            sqlite3_finalize(stmt);
            return send_json(connection, "{\"error\":\"Response too large\"}", MHD_HTTP_INTERNAL_SERVER_ERROR);
        }

        offset += written;
        first = 0;
    }

    sqlite3_finalize(stmt);

    if (offset + 2 >= sizeof(json)) {
        return send_json(connection, "{\"error\":\"Response too large\"}", MHD_HTTP_INTERNAL_SERVER_ERROR);
    }

    snprintf(json + offset, sizeof(json) - offset, "]");

    return send_json(connection, json, MHD_HTTP_OK);
}

int parse_and_validate_user(const char *body,
                            char *username,
                            char *email,
                            char *role) {
    if (!body) {
        return 0;
    }

    if (!extract_json_value(body, "username", username, MAX_USERNAME + 1) ||
        !extract_json_value(body, "email", email, MAX_EMAIL + 1) ||
        !extract_json_value(body, "role", role, MAX_ROLE + 1)) {
        return 0;
    }

    if (!is_valid_username(username)) {
        return 0;
    }

    if (!is_valid_email(email)) {
        return 0;
    }

    if (!is_valid_role(role)) {
        return 0;
    }

    return 1;
}

int handle_create_user(struct MHD_Connection *connection, const char *body) {
    char username[MAX_USERNAME + 1];
    char email[MAX_EMAIL + 1];
    char role[MAX_ROLE + 1];

    if (!parse_and_validate_user(body, username, email, role)) {
        return send_json(connection, "{\"error\":\"Invalid input\"}", MHD_HTTP_BAD_REQUEST);
    }

    const char *sql =
        "INSERT INTO users(username, email, role) VALUES (?, ?, ?);";

    sqlite3_stmt *stmt = NULL;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return send_json(connection, "{\"error\":\"Database error\"}", MHD_HTTP_INTERNAL_SERVER_ERROR);
    }

    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, email, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, role, -1, SQLITE_TRANSIENT);

    int rc = sqlite3_step(stmt);
    sqlite3_finalize(stmt);

    if (rc != SQLITE_DONE) {
        return send_json(connection, "{\"error\":\"Could not create user\"}", MHD_HTTP_CONFLICT);
    }

    return send_json(connection, "{\"message\":\"User created\"}", MHD_HTTP_CREATED);
}

int handle_update_user(struct MHD_Connection *connection, const char *body) {
    const char *id = MHD_lookup_connection_value(connection, MHD_GET_ARGUMENT_KIND, "id");

    if (!is_valid_id(id)) {
        return send_json(connection, "{\"error\":\"Invalid or missing user id\"}", MHD_HTTP_BAD_REQUEST);
    }

    char username[MAX_USERNAME + 1];
    char email[MAX_EMAIL + 1];
    char role[MAX_ROLE + 1];

    if (!parse_and_validate_user(body, username, email, role)) {
        return send_json(connection, "{\"error\":\"Invalid input\"}", MHD_HTTP_BAD_REQUEST);
    }

    const char *sql =
        "UPDATE users SET username = ?, email = ?, role = ? WHERE id = ?;";

    sqlite3_stmt *stmt = NULL;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return send_json(connection, "{\"error\":\"Database error\"}", MHD_HTTP_INTERNAL_SERVER_ERROR);
    }

    sqlite3_bind_text(stmt, 1, username, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 2, email, -1, SQLITE_TRANSIENT);
    sqlite3_bind_text(stmt, 3, role, -1, SQLITE_TRANSIENT);
    sqlite3_bind_int(stmt, 4, atoi(id));

    int rc = sqlite3_step(stmt);
    int changed = sqlite3_changes(db);

    sqlite3_finalize(stmt);

    if (rc != SQLITE_DONE) {
        return send_json(connection, "{\"error\":\"Could not update user\"}", MHD_HTTP_CONFLICT);
    }

    if (changed == 0) {
        return send_json(connection, "{\"error\":\"User not found\"}", MHD_HTTP_NOT_FOUND);
    }

    return send_json(connection, "{\"message\":\"User updated\"}", MHD_HTTP_OK);
}

int handle_delete_user(struct MHD_Connection *connection) {
    const char *id = MHD_lookup_connection_value(connection, MHD_GET_ARGUMENT_KIND, "id");

    if (!is_valid_id(id)) {
        return send_json(connection, "{\"error\":\"Invalid or missing user id\"}", MHD_HTTP_BAD_REQUEST);
    }

    const char *sql = "DELETE FROM users WHERE id = ?;";

    sqlite3_stmt *stmt = NULL;

    if (sqlite3_prepare_v2(db, sql, -1, &stmt, NULL) != SQLITE_OK) {
        return send_json(connection, "{\"error\":\"Database error\"}", MHD_HTTP_INTERNAL_SERVER_ERROR);
    }

    sqlite3_bind_int(stmt, 1, atoi(id));

    int rc = sqlite3_step(stmt);
    int changed = sqlite3_changes(db);

    sqlite3_finalize(stmt);

    if (rc != SQLITE_DONE) {
        return send_json(connection, "{\"error\":\"Could not delete user\"}", MHD_HTTP_INTERNAL_SERVER_ERROR);
    }

    if (changed == 0) {
        return send_json(connection, "{\"error\":\"User not found\"}", MHD_HTTP_NOT_FOUND);
    }

    return send_json(connection, "{\"message\":\"User deleted\"}", MHD_HTTP_OK);
}

int request_handler(void *cls,
                    struct MHD_Connection *connection,
                    const char *url,
                    const char *method,
                    const char *version,
                    const char *upload_data,
                    size_t *upload_data_size,
                    void **con_cls) {
    (void)cls;
    (void)version;

    if (strcmp(url, "/users") != 0) {
        return send_json(connection, "{\"error\":\"Not found\"}", MHD_HTTP_NOT_FOUND);
    }

    if (*con_cls == NULL) {
        struct RequestData *req = calloc(1, sizeof(struct RequestData));

        if (!req) {
            return MHD_NO;
        }

        *con_cls = req;
        return MHD_YES;
    }

    struct RequestData *req = *con_cls;

    if (*upload_data_size != 0) {
        if (req->size + *upload_data_size > MAX_BODY_SIZE) {
            free(req->body);
            free(req);
            *con_cls = NULL;

            return send_json(connection, "{\"error\":\"Request body too large\"}", MHD_HTTP_PAYLOAD_TOO_LARGE);
        }

        char *new_body = realloc(req->body, req->size + *upload_data_size + 1);

        if (!new_body) {
            free(req->body);
            free(req);
            *con_cls = NULL;

            return MHD_NO;
        }

        req->body = new_body;

        memcpy(req->body + req->size, upload_data, *upload_data_size);
        req->size += *upload_data_size;
        req->body[req->size] = '\0';

        *upload_data_size = 0;
        return MHD_YES;
    }

    int ret;

    if (strcmp(method, "GET") == 0) {
        ret = handle_get_users(connection);
    } else if (strcmp(method, "POST") == 0) {
        ret = handle_create_user(connection, req->body);
    } else if (strcmp(method, "PUT") == 0) {
        ret = handle_update_user(connection, req->body);
    } else if (strcmp(method, "DELETE") == 0) {
        ret = handle_delete_user(connection);
    } else {
        ret = send_json(connection, "{\"error\":\"Method not allowed\"}", MHD_HTTP_METHOD_NOT_ALLOWED);
    }

    free(req->body);
    free(req);
    *con_cls = NULL;

    return ret;
}

int main() {
    if (sqlite3_open(DB_FILE, &db) != SQLITE_OK) {
        fprintf(stderr, "Cannot open database\n");
        return 1;
    }

    sqlite3_exec(db, "PRAGMA foreign_keys = ON;", NULL, NULL, NULL);

    if (!init_db()) {
        sqlite3_close(db);
        return 1;
    }

    struct MHD_Daemon *server =
        MHD_start_daemon(MHD_USE_INTERNAL_POLLING_THREAD,
                         PORT,
                         NULL,
                         NULL,
                         &request_handler,
                         NULL,
                         MHD_OPTION_END);

    if (!server) {
        fprintf(stderr, "Failed to start server\n");
        sqlite3_close(db);
        return 1;
    }

    printf("Secure C REST API running on http://localhost:%d/users\n", PORT);
    getchar();

    MHD_stop_daemon(server);
    sqlite3_close(db);

    return 0;
}