#include <stdio.h>
#include <string.h>

#define MAX_USERS 100
#define MAX_USERNAME 50
#define MAX_PASSWORD 50

typedef struct {
    char username[MAX_USERNAME];
    char password[MAX_PASSWORD];
} User;

User users[MAX_USERS];
int user_count = 0;

int store_password(char *username, char *password) {
    if (user_count >= MAX_USERS) {
        return -1;
    }

    strcpy(users[user_count].username, username);
    strcpy(users[user_count].password, password);

    user_count++;

    return 0;
}