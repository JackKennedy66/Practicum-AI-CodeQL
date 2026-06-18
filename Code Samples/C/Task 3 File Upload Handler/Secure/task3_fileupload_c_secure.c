#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>

#define UPLOAD_DIR "./uploads/"
#define MAX_FILENAME_LEN 100
#define MAX_FILE_SIZE 1048576   /* 1 MB */
#define BUFFER_SIZE 4096

int is_valid_filename(const char *filename) {
    size_t len = strlen(filename);

    if (len == 0 || len > MAX_FILENAME_LEN) {
        return 0;
    }

    if (strstr(filename, "..") != NULL ||
        strchr(filename, '/') != NULL ||
        strchr(filename, '\\') != NULL) {
        return 0;
    }

    for (size_t i = 0; i < len; i++) {
        if (!isalnum((unsigned char)filename[i]) &&
            filename[i] != '_' &&
            filename[i] != '-' &&
            filename[i] != '.') {
            return 0;
        }
    }

    return 1;
}

int has_allowed_extension(const char *filename) {
    const char *ext = strrchr(filename, '.');

    if (ext == NULL) {
        return 0;
    }

    return strcmp(ext, ".txt") == 0 ||
           strcmp(ext, ".pdf") == 0 ||
           strcmp(ext, ".png") == 0 ||
           strcmp(ext, ".jpg") == 0;
}

int upload_file(const char *filename) {
    char filepath[512];
    FILE *output;
    char buffer[BUFFER_SIZE];
    size_t bytes_read;
    size_t total_bytes = 0;

    if (!is_valid_filename(filename)) {
        printf("Content-Type: text/plain\n\n");
        printf("Error: Invalid filename.\n");
        return 1;
    }

    if (!has_allowed_extension(filename)) {
        printf("Content-Type: text/plain\n\n");
        printf("Error: File type not allowed.\n");
        return 1;
    }

    if (snprintf(filepath, sizeof(filepath), "%s%s", UPLOAD_DIR, filename) >= sizeof(filepath)) {
        printf("Content-Type: text/plain\n\n");
        printf("Error: File path too long.\n");
        return 1;
    }

    output = fopen(filepath, "wbx");
    if (output == NULL) {
        printf("Content-Type: text/plain\n\n");
        printf("Error: Could not save uploaded file.\n");
        return 1;
    }

    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, stdin)) > 0) {
        total_bytes += bytes_read;

        if (total_bytes > MAX_FILE_SIZE) {
            fclose(output);
            remove(filepath);

            printf("Content-Type: text/plain\n\n");
            printf("Error: File exceeds maximum allowed size.\n");
            return 1;
        }

        if (fwrite(buffer, 1, bytes_read, output) != bytes_read) {
            fclose(output);
            remove(filepath);

            printf("Content-Type: text/plain\n\n");
            printf("Error: Failed while writing file.\n");
            return 1;
        }
    }

    if (ferror(stdin)) {
        fclose(output);
        remove(filepath);

        printf("Content-Type: text/plain\n\n");
        printf("Error: Failed while reading uploaded file.\n");
        return 1;
    }

    fclose(output);

    printf("Content-Type: text/plain\n\n");
    printf("File uploaded successfully.\n");

    return 0;
}

int main(void) {
    char *filename = getenv("HTTP_X_FILENAME");

    if (filename == NULL) {
        printf("Content-Type: text/plain\n\n");
        printf("Error: No filename provided.\n");
        return 1;
    }

    return upload_file(filename);
}