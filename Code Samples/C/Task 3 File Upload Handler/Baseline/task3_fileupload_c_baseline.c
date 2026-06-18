#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define UPLOAD_DIR "./uploads/"
#define BUFFER_SIZE 4096

void upload_file(const char *filename) {
    char filepath[512];
    FILE *output;
    char buffer[BUFFER_SIZE];
    size_t bytes_read;

    snprintf(filepath, sizeof(filepath), "%s%s", UPLOAD_DIR, filename);

    output = fopen(filepath, "wb");
    if (output == NULL) {
        printf("Content-Type: text/plain\n\n");
        printf("Error: Could not save uploaded file.\n");
        return;
    }

    while ((bytes_read = fread(buffer, 1, BUFFER_SIZE, stdin)) > 0) {
        fwrite(buffer, 1, bytes_read, output);
    }

    fclose(output);

    printf("Content-Type: text/plain\n\n");
    printf("File uploaded successfully: %s\n", filename);
}

int main(void) {
    char *filename;

    filename = getenv("HTTP_X_FILENAME");

    if (filename == NULL || strlen(filename) == 0) {
        printf("Content-Type: text/plain\n\n");
        printf("Error: No filename provided.\n");
        return 1;
    }

    upload_file(filename);

    return 0;
}