#include <stdio.h>
#include <string.h>
#include <ctype.h>

#define MAX_USERNAME 30
#define MAX_PASSWORD 64

int is_valid_username(const char *username) {
    int len = strlen(username);

    if (len < 3 || len >= MAX_USERNAME) {
        return 0;
    }

    for (int i = 0; i < len; i++) {
        if (!isalnum(username[i]) && username[i] != '_') {
            return 0;
        }
    }

    return 1;
}

int authenticate(const char *username, const char *password) {
    /*
      In a real system, passwords should be stored as salted hashes,
      not plain text. This is simplified for demonstration.
    */
    const char storedUsername[] = "admin";
    const char storedPassword[] = "StrongPassword123!";

    if (strcmp(username, storedUsername) == 0 &&
        strcmp(password, storedPassword) == 0) {
        return 1;
    }

    return 0;
}

void remove_newline(char *input) {
    input[strcspn(input, "\n")] = '\0';
}

int main() {
    char username[MAX_USERNAME];
    char password[MAX_PASSWORD];

    printf("Enter username: ");
    if (fgets(username, sizeof(username), stdin) == NULL) {
        printf("Input error.\n");
        return 1;
    }
    remove_newline(username);

    if (!is_valid_username(username)) {
        printf("Invalid username format.\n");
        return 1;
    }

    printf("Enter password: ");
    if (fgets(password, sizeof(password), stdin) == NULL) {
        printf("Input error.\n");
        return 1;
    }
    remove_newline(password);

    if (strlen(password) < 8 || strlen(password) >= MAX_PASSWORD) {
        printf("Invalid password length.\n");
        return 1;
    }

    if (authenticate(username, password)) {
        printf("Login successful.\n");
    } else {
        printf("Invalid username or password.\n");
    }

    memset(password, 0, sizeof(password));

    return 0;
}