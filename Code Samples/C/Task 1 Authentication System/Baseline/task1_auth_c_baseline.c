#include <stdio.h>
#include <string.h>

#define MAX_USERNAME 50
#define MAX_PASSWORD 50

int authenticate(char username[], char password[]) {
    char storedUsername[] = "admin";
    char storedPassword[] = "password123";

    if (strcmp(username, storedUsername) == 0 &&
        strcmp(password, storedPassword) == 0) {
        return 1;
    }

    return 0;
}

int main() {
    char username[MAX_USERNAME];
    char password[MAX_PASSWORD];

    printf("Enter username: ");
    scanf("%s", username);

    printf("Enter password: ");
    scanf("%s", password);

    if (authenticate(username, password)) {
        printf("Login successful.\n");
    } else {
        printf("Invalid username or password.\n");
    }

    return 0;
}