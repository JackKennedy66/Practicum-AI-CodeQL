#include <stdio.h>
#include <string.h>
#include <ctype.h>
#include <stdlib.h>

#define MAX_FILENAME_LEN 100
#define MAX_LINE_LEN 1024
#define BASE_DIR "files/"

int is_valid_filename(const char *filename) {
    size_t len = strlen(filename);

    if (len == 0 || len > MAX_FILENAME_LEN) {
        return 0;
    }

    for (size_t i = 0; i < len; i++) {
        if (!(isalnum((unsigned char)filename[i]) ||
              filename[i] == '_' ||
              filename[i] == '-' ||
              filename[i] == '.')) {
            return 0;
        }
    }

    if (strstr(filename, "..") != NULL) {
        return 0;
    }

    return 1;
}

int main(void) {
    char filename[MAX_FILENAME_LEN + 1];
    char filepath[256];
    char line[MAX_LINE_LEN];

    printf("Enter filename to view: ");

    if (fgets(filename, sizeof(filename), stdin) == NULL) {
        fprintf(stderr, "Input error.\n");
        return 1;
    }

    filename[strcspn(filename, "\n")] = '\0';

    if (!is_valid_filename(filename)) {
        fprintf(stderr, "Invalid filename.\n");
        return 1;
    }

    if (snprintf(filepath, sizeof(filepath), "%s%s", BASE_DIR, filename) >= sizeof(filepath)) {
        fprintf(stderr, "File path too long.\n");
        return 1;
    }

    FILE *file = fopen(filepath, "r");

    if (file == NULL) {
        fprintf(stderr, "File could not be opened.\n");
        return 1;
    }

    printf("\n--- File Contents ---\n");

    while (fgets(line, sizeof(line), file) != NULL) {
        fputs(line, stdout);
    }

    fclose(file);

    return 0;
}