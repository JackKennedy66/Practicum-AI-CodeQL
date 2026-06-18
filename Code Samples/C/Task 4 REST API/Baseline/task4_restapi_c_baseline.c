/*
 * Simple C REST API for User Management
 * Uses libmicrohttpd and SQLite.
 *
 * Endpoints:
 *   GET    /users
 *   GET    /users?id=1
 *   POST   /users
 *   PUT    /users?id=1
 *   DELETE /users?id=1
 *
 * Compile:
 *   gcc user_api.c -o user_api -lmicrohttpd -lsqlite3
 *
 * Run:
 *   ./user_api
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sqlite3.h>
#include <microhttpd.h>

#define PORT 8080
#define DB_FILE "users.db"

sqlite3 *db;

void init_db() {
    char *err = NULL;

    const char *sql =
        "CREATE TABLE IF NOT EXISTS users ("
        "id INTEGER PRIMARY KEY AUTOINCREMENT,"
        "username TEXT NOT NULL,"
        "email TEXT NOT NULL,"
        "role TEXT NOT NULL);";

    if (sqlite3_exec(db, sql, NULL, NULL, &err) != SQLITE_OK) {
        fprintf(stderr, "Database error: %s\n", err);
        sqlite3_free(err);
        exit(1);
    }
}

int send_response(struct MHD_Connection *connection, const char *body, int status) {
    struct MHD_Response *response =
        MHD_create_response_from_buffer(strlen(body), (void *)body, MHD_RESPMEM_MUST_COPY);

    MHD_add_response_header(response, "Content-Type", "application/json");

    int ret = MHD_queue_response(connection, status, response);
    MHD_destroy_response(response);

    return ret;
}

int handle_get_users(struct MHD_Connection *connection) {
    const char *id = MHD_lookup_connection_value(connection, MHD_GET_ARGUMENT_KIND, "id");

    char sql[512];

    if (id) {
        sprintf(sql, "SELECT id, username, email, role FROM users WHERE id = %s;", id);
    } else {
        sprintf(sql, "SELECT id, username, email, role FROM users;");
    }

    sqlite3_stmt *stmt;
    sqlite3_prepare_v2(db, sql, -1, &stmt, NULL);

    char json[4096] = "[";
    int first = 1;

    while (sqlite3_step(stmt) == SQLITE_ROW) {
        char user[512];

        sprintf(user,
                "%s{\"id\":%d,\"username\":\"%s\",\"email\":\"%s\",\"role\":\"%s\"}",
                first ? "" : ",",
                sqlite3_column_int(stmt, 0),
                sqlite3_column_text(stmt, 1),
                sqlite3_column_text(stmt, 2),
                sqlite3_column_text(stmt, 3));

        strcat(json, user);
        first = 0;
    }

    strcat(json, "]");
    sqlite3_finalize(stmt);

    return send_response(connection, json, MHD_HTTP_OK);
}

int handle_create_user(struct MHD_Connection *connection, const char *data) {
    char username[100], email[100], role[50];

    sscanf(data,
           "{\"username\":\"%99[^\"]\",\"email\":\"%99[^\"]\",\"role\":\"%49[^\"]\"}",
           username, email, role);

    char sql[512];
    sprintf(sql,
            "INSERT INTO users(username, email, role) VALUES('%s', '%s', '%s');",
            username, email, role);

    char *err = NULL;

    if (sqlite3_exec(db, sql, NULL, NULL, &err) != SQLITE_OK) {
        sqlite3_free(err);
        return send_response(connection, "{\"error\":\"Could not create user\"}", MHD_HTTP_BAD_REQUEST);
    }

    return send_response(connection, "{\"message\":\"User created\"}", MHD_HTTP_CREATED);
}

int handle_update_user(struct MHD_Connection *connection, const char *data) {
    const char *id = MHD_lookup_connection_value(connection, MHD_GET_ARGUMENT_KIND, "id");

    if (!id) {
        return send_response(connection, "{\"error\":\"Missing user id\"}", MHD_HTTP_BAD_REQUEST);
    }

    char username[100], email[100], role[50];

    sscanf(data,
           "{\"username\":\"%99[^\"]\",\"email\":\"%99[^\"]\",\"role\":\"%49[^\"]\"}",
           username, email, role);

    char sql[512];
    sprintf(sql,
            "UPDATE users SET username='%s', email='%s', role='%s' WHERE id=%s;",
            username, email, role, id);

    char *err = NULL;

    if (sqlite3_exec(db, sql, NULL, NULL, &err) != SQLITE_OK) {
        sqlite3_free(err);
        return send_response(connection, "{\"error\":\"Could not update user\"}", MHD_HTTP_BAD_REQUEST);
    }

    return send_response(connection, "{\"message\":\"User updated\"}", MHD_HTTP_OK);
}

int handle_delete_user(struct MHD_Connection *connection) {
    const char *id = MHD_lookup_connection_value(connection, MHD_GET_ARGUMENT_KIND, "id");

    if (!id) {
        return send_response(connection, "{\"error\":\"Missing user id\"}", MHD_HTTP_BAD_REQUEST);
    }

    char sql[256];
    sprintf(sql, "DELETE FROM users WHERE id=%s;", id);

    char *err = NULL;

    if (sqlite3_exec(db, sql, NULL, NULL, &err) != SQLITE_OK) {
        sqlite3_free(err);
        return send_response(connection, "{\"error\":\"Could not delete user\"}", MHD_HTTP_BAD_REQUEST);
    }

    return send_response(connection, "{\"message\":\"User deleted\"}", MHD_HTTP_OK);
}

struct RequestData {
    char *data;
    size_t size;
};

int request_handler(void *cls,
                    struct MHD_Connection *connection,
                    const char *url,
                    const char *method,
                    const char *version,
                    const char *upload_data,
                    size_t *upload_data_size,
                    void **con_cls) {
    if (strcmp(url, "/users") != 0) {
        return send_response(connection, "{\"error\":\"Not found\"}", MHD_HTTP_NOT_FOUND);
    }

    if (*con_cls == NULL) {
        struct RequestData *req = calloc(1, sizeof(struct RequestData));
        *con_cls = req;
        return MHD_YES;
    }

    struct RequestData *req = *con_cls;

    if (*upload_data_size != 0) {
        req->data = realloc(req->data, req->size + *upload_data_size + 1);
        memcpy(req->data + req->size, upload_data, *upload_data_size);
        req->size += *upload_data_size;
        req->data[req->size] = '\0';

        *upload_data_size = 0;
        return MHD_YES;
    }

    int ret;

    if (strcmp(method, "GET") == 0) {
        ret = handle_get_users(connection);
    } else if (strcmp(method, "POST") == 0) {
        ret = handle_create_user(connection, req->data);
    } else if (strcmp(method, "PUT") == 0) {
        ret = handle_update_user(connection, req->data);
    } else if (strcmp(method, "DELETE") == 0) {
        ret = handle_delete_user(connection);
    } else {
        ret = send_response(connection, "{\"error\":\"Method not allowed\"}", MHD_HTTP_METHOD_NOT_ALLOWED);
    }

    free(req->data);
    free(req);
    *con_cls = NULL;

    return ret;
}

int main() {
    if (sqlite3_open(DB_FILE, &db) != SQLITE_OK) {
        fprintf(stderr, "Cannot open database\n");
        return 1;
    }

    init_db();

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

    printf("C REST API running on http://localhost:%d/users\n", PORT);
    getchar();

    MHD_stop_daemon(server);
    sqlite3_close(db);

    return 0;
}